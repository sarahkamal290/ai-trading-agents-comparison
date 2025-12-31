"""FinGPT - Financial AI Trading System"""
import openai
import json
from framework.simulator.base_agent import BaseTradingAgent

class FinGPTAgent(BaseTradingAgent):
    """FinGPT-based trading with sentiment and prediction"""
    
    def __init__(self, agent_id, name, starting_cash):
        super().__init__(agent_id, name, starting_cash)
        self.model = "gpt-3.5-turbo"
        self.risk_tolerance = 0.5
        self.decisions = []
        
    def on_tick(self, current_time, simulator):
        """FinGPT workflow: Sentiment  Prediction  Risk  Decision"""
        
        market_data = simulator.get_market_data("STOCK")
        current_price = market_data["mid_price"]
        
        if not current_price:
            return
        
        try:
            # Step 1: Sentiment analysis
            sentiment = self._analyze_sentiment(current_price)
            
            # Step 2: Price prediction
            prediction = self._predict_price(current_price, sentiment)
            
            # Step 3: Risk assessment
            risk = self._assess_risk(current_price, prediction)
            
            # Step 4: Trading decision
            decision = self._make_decision(current_price, sentiment, prediction, risk)
            
            # Execute
            self._execute_decision(decision, simulator, current_price)
            
        except Exception as e:
            print(f"{self.name} error: {e}")
    
    def _analyze_sentiment(self, price):
        """Analyze market sentiment"""
        prompt = f"""Analyze market sentiment for stock at ${price:.2f}.
Return JSON:
{{"sentiment": <-1 to 1>, "confidence": <0 to 1>}}"""
        
        return self._call_llm(prompt)
    
    def _predict_price(self, price, sentiment):
        """Predict price movement"""
        sent_score = sentiment.get("sentiment", 0)
        
        prompt = f"""Predict price movement for stock at ${price:.2f}.
Market sentiment: {sent_score:.2f}

Return JSON:
{{"expected_change_pct": <percentage>, "confidence": <0-1>}}"""
        
        return self._call_llm(prompt)
    
    def _assess_risk(self, price, prediction):
        """Assess trading risk"""
        portfolio_value = self.cash + self.positions.get("STOCK", 0) * price
        
        prompt = f"""Assess risk for this trade.
Portfolio Value: ${portfolio_value:.2f}
Expected Change: {prediction.get('expected_change_pct', 0):.1f}%
Risk Tolerance: {self.risk_tolerance}

Return JSON:
{{"risk_score": <0-1>, "recommended_size_pct": <0-100>}}"""
        
        return self._call_llm(prompt)
    
    def _make_decision(self, price, sentiment, prediction, risk):
        """Make final trading decision"""
        expected_change = prediction.get("expected_change_pct", 0)
        recommended_size = risk.get("recommended_size_pct", 20)
        
        prompt = f"""Make trading decision.
Price: ${price:.2f}
Expected Change: {expected_change:.1f}%
Risk Score: {risk.get('risk_score', 0.5):.2f}
Recommended Position: {recommended_size:.0f}% of portfolio
Cash Available: ${self.cash:.2f}
Current Position: {self.positions.get('STOCK', 0)} shares

Return JSON:
{{"action": "buy|sell|hold", "quantity": <number>, "reasoning": "<brief>"}}"""
        
        return self._call_llm(prompt)
    
    def _execute_decision(self, decision, simulator, current_price):
        """Execute trading decision"""
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        
        if action == "buy" and quantity > 0:
            max_affordable = int(self.cash / current_price)
            quantity = min(quantity, max_affordable)
            quantity = int(quantity * self.risk_tolerance)
            if quantity > 0:
                simulator.submit_order(self.agent_id, "STOCK", "BUY", quantity, current_price)
        
        elif action == "sell" and quantity > 0:
            current_position = self.positions.get("STOCK", 0)
            quantity = min(quantity, current_position)
            if quantity > 0:
                simulator.submit_order(self.agent_id, "STOCK", "SELL", quantity, current_price)
        
        self.decisions.append(decision)
    
    def _call_llm(self, prompt):
        """Call FinGPT (using GPT-3.5 as proxy)"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are FinGPT, a financial AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=250
            )
            
            content = response.choices[0].message.content
            start = content.find("{")
            end = content.rfind("}") + 1
            
            if start != -1 and end > start:
                return json.loads(content[start:end])
            return {}
        except:
            return {}
