"""StockAgent - Behavioral Finance Multi-Agent System"""
import openai
import json
from framework.simulator.base_agent import BaseTradingAgent

class StockAgentTrader(BaseTradingAgent):
    """Individual investor with personality-driven trading"""
    
    PERSONALITIES = ["Conservative", "Aggressive", "Balanced", "Growth-Oriented"]
    
    def __init__(self, agent_id, name, starting_cash, personality="Balanced"):
        super().__init__(agent_id, name, starting_cash)
        self.personality = personality if personality in self.PERSONALITIES else "Balanced"
        self.llm_model = "gpt-3.5-turbo"
        self.decisions = []
        
    def on_tick(self, current_time, simulator):
        """Make trading decision based on personality"""
        
        market_data = simulator.get_market_data("STOCK")
        current_price = market_data["mid_price"]
        
        if not current_price:
            return
        
        # Build personality-based prompt
        prompt = self._build_prompt(current_price, market_data)
        
        try:
            decision = self._call_llm(prompt)
            self._execute_decision(decision, simulator, current_price)
        except Exception as e:
            print(f"{self.name} error: {e}")
    
    def _build_prompt(self, current_price, market_data):
        traits = {
            "Conservative": "risk-averse, prefer stable returns, avoid excessive trading",
            "Aggressive": "risk-seeking, pursue high returns, willing to trade frequently",
            "Balanced": "moderate risk tolerance, balanced approach",
            "Growth-Oriented": "focus on long-term growth, patient"
        }
        
        return f"""You are a {self.personality} stock trader.
Personality: {traits[self.personality]}

Current Situation:
- Stock Price: ${current_price:.2f}
- Your Cash: ${self.cash:.2f}
- Your Position: {self.positions.get('STOCK', 0)} shares
- Portfolio Value: ${self.cash + self.positions.get('STOCK', 0) * current_price:.2f}

Decide: BUY, SELL, or HOLD

Respond in JSON:
{{"action": "buy|sell|hold", "quantity": <number>, "reasoning": "<brief explanation>"}}"""
    
    def _call_llm(self, prompt):
        """Call GPT for decision"""
        response = openai.ChatCompletion.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": f"You are a {self.personality} trader."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
        
        return {"action": "hold", "quantity": 0}
    
    def _execute_decision(self, decision, simulator, current_price):
        """Execute trading decision"""
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
