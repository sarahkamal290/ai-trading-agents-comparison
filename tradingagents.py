"""TradingAgents - Institutional Trading Firm System"""
import openai
import json
from framework.simulator.base_agent import BaseTradingAgent

class TradingAgentsSystem(BaseTradingAgent):
    """Multi-specialist institutional trading system"""
    
    def __init__(self, agent_id, name, starting_cash):
        super().__init__(agent_id, name, starting_cash)
        self.quick_llm = "gpt-3.5-turbo"
        self.deep_llm = "gpt-4o-mini"  # Using available model
        self.analyst_reports = []
        self.decisions = []
        
    def on_tick(self, current_time, simulator):
        """Full institutional workflow"""
        
        market_data = simulator.get_market_data("STOCK")
        current_price = market_data["mid_price"]
        
        if not current_price:
            return
        
        try:
            # Step 1: Analyst reports
            fundamental = self._fundamental_analysis(current_price)
            technical = self._technical_analysis(current_price, market_data)
            
            # Step 2: Trader decision
            decision = self._trader_decision(current_price, fundamental, technical)
            
            # Step 3: Risk management
            final_decision = self._risk_management(decision, current_price)
            
            # Step 4: Execute
            self._execute_decision(final_decision, simulator, current_price)
            
        except Exception as e:
            print(f"{self.name} error: {e}")
    
    def _fundamental_analysis(self, price):
        """Fundamental analyst report"""
        prompt = f"""As a Fundamental Analyst, analyze this stock at ${price:.2f}.
Provide brief analysis in JSON:
{{"outlook": "bullish|bearish|neutral", "key_points": ["point1", "point2"]}}"""
        
        return self._call_llm(prompt, self.quick_llm)
    
    def _technical_analysis(self, price, market_data):
        """Technical analyst report"""
        prompt = f"""As a Technical Analyst, analyze this stock at ${price:.2f}.
Market has {len(market_data.get('bids', []))} bid levels, {len(market_data.get('asks', []))} ask levels.
Provide analysis in JSON:
{{"trend": "up|down|sideways", "recommendation": "buy|sell|hold"}}"""
        
        return self._call_llm(prompt, self.quick_llm)
    
    def _trader_decision(self, price, fundamental, technical):
        """Trader synthesizes information"""
        prompt = f"""You are the Lead Trader. Make final decision.

Fundamental Analyst: {fundamental.get('outlook', 'neutral')}
Technical Analyst: {technical.get('recommendation', 'hold')}

Current Price: ${price:.2f}
Your Cash: ${self.cash:.2f}
Your Position: {self.positions.get('STOCK', 0)} shares

Decide trade in JSON:
{{"action": "buy|sell|hold", "quantity": <number>, "confidence": <0-1>}}"""
        
        return self._call_llm(prompt, self.deep_llm)
    
    def _risk_management(self, decision, price):
        """Risk team validates decision"""
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        
        # Apply 30% position limit
        portfolio_value = self.cash + self.positions.get("STOCK", 0) * price
        max_position_value = portfolio_value * 0.3
        max_quantity = int(max_position_value / price) if price > 0 else 0
        
        adjusted_quantity = min(quantity, max_quantity)
        
        return {
            "action": action,
            "quantity": adjusted_quantity,
            "original_quantity": quantity
        }
    
    def _execute_decision(self, decision, simulator, current_price):
        """Execute validated decision"""
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        
        if action == "buy" and quantity > 0:
            max_affordable = int(self.cash / current_price)
            quantity = min(quantity, max_affordable)
            if quantity > 0:
                simulator.submit_order(self.agent_id, "STOCK", "BUY", quantity, current_price)
        
        elif action == "sell" and quantity > 0:
            current_position = self.positions.get("STOCK", 0)
            quantity = min(quantity, current_position)
            if quantity > 0:
                simulator.submit_order(self.agent_id, "STOCK", "SELL", quantity, current_price)
        
        self.decisions.append(decision)
    
    def _call_llm(self, prompt, model):
        """Call LLM API"""
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            start = content.find("{")
            end = content.rfind("}") + 1
            
            if start != -1 and end > start:
                return json.loads(content[start:end])
            return {}
        except:
            return {}
