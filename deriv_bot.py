import websocket
import json
import threading
import time

class DerivBot:
    def __init__(self, token, stake, martingale_factor, max_losses, profit_target, stop_loss_value):
        self.token = token
        self.stake = stake
        self.current_stake = stake
        self.martingale_factor = martingale_factor
        self.max_losses = max_losses
        self.profit_target = profit_target
        self.stop_loss_value = stop_loss_value

        self.ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
        self.ws = None
        self.digits = []
        self.authorized = False

        self.loss_streak = 0
        self.total_profit = 0

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.start()
        time.sleep(2)

    def on_open(self, ws):
        ws.send(json.dumps({"authorize": self.token}))
        ws.send(json.dumps({"ticks": "R_100"}))

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'authorize' in data:
            self.authorized = True
            print("✅ Autenticado com sucesso.")
        if 'tick' in data:
            last_digit = int(str(data['tick']['quote'])[-1])
            self.digits.append(last_digit)
            if len(self.digits) > 10:
                self.digits.pop(0)

    def on_error(self, ws, error):
        print(f"Erro: {error}")

    def on_close(self, ws, code, msg):
        print("🔌 Conexão encerrada.")

    def should_enter_trade(self):
        return len(self.digits) == 10 and sum(1 for d in self.digits if d > 7) >= 5

    def place_trade(self):
        contract = {
            "buy": 1,
            "price": round(self.current_stake, 2),
            "parameters": {
                "amount": round(self.current_stake, 2),
                "basis": "stake",
                "contract_type": "DIGITOVER",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": "7"
            },
            "passthrough": {},
            "req_id": 1
        }
        self.ws.send(json.dumps(contract))

    def run(self):
        self.connect()
        print("▶️ Robô iniciado...")
        while True:
            if self.total_profit >= self.profit_target:
                print("🎉 Meta de lucro atingida! Robô encerrado.")
                break
            if self.loss_streak >= self.max_losses:
                print("⛔ Limite de perdas consecutivas atingido!")
                break
            if self.total_profit <= -abs(self.stop_loss_value):
                print("🛑 Stop Loss de valor atingido!")
                break
            if self.should_enter_trade():
                print("🎯 Critério atendido! Entrando em Over 7...")
                self.place_trade()
                time.sleep(5)
                import random
                result = random.choice(["win", "loss"])
                print(f"🎲 Resultado: {result}")
                if result == "loss":
                    self.total_profit -= self.current_stake
                    self.current_stake *= self.martingale_factor
                    self.loss_streak += 1
                else:
                    self.total_profit += self.current_stake * 0.8
                    self.current_stake = self.stake
                    self.loss_streak = 0
                    self.digits = []
                print(f"📊 Lucro: {round(self.total_profit, 2)} | Perdas: {self.loss_streak}")
            time.sleep(1)