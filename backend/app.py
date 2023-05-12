import copy
import json
import time
from threading import Thread

import requests
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin

from TicTacToeAi import TicTacToeAI
from TicTacToeAi import Piece

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

host = 'http://localhost:5000'  # Địa chỉ server trọng tài mặc định
team_id = 123 # team_id mặc định
game_info = {}  # Thông tin trò chơi để hiển thị trên giao diện
stop_thread = False  # Biến dùng để dừng thread lắng nghe

ai = TicTacToeAI(Piece.ALLY)  # Khởi tạo AI chạy mặc định với đội X


# Giao tiếp với trọng tài qua API:
# nghe trọng tài trả về thông tin hiển thị ở '/', gửi yêu cầu khởi tại qua '/init/' và gửi nước đi qua '/move'
class GameClient:
    def __init__(self, server_url, your_team_id, your_team_roles):
        self.server_url = server_url
        self.team_id = f'{your_team_id}+{your_team_roles}'
        self.team_roles = your_team_roles
        self.match_id = None
        self.board = None
        self.init = None
        self.size = None
        self.ai = None
        self.room_id = None

    def listen(self):
        # Lắng nghe yêu cầu từ server trọng tài
        # và cập nhật thông tin trò chơi
        while not stop_thread:
            # Thời gian lắng nghe giữa các lần
            time.sleep(3)
            print(f'Init: {self.init}')

            # Nếu chưa kết nối thì gửi yêu cầu kết nối
            if not self.init:
                response = self.send_init()
            else:
                response = self.fetch_game_info()

            # Lấy thông tin trò chơi từ server trọng tài và cập nhật vào game_info
            data = json.loads(response.content)
            global game_info
            game_info = data.copy()

            # Nếu chưa có id phòng thì tiếp tục gửi yêu cầu
            if data.get("room_id") is None:
                print(data)
                continue
            # Khởi tạo trò chơi
            if data.get("init"):
                print("Connection established")
                self.init = True
                self.room_id = data.get("room_id")

            # Nhận thông tin trò chơi
            elif data.get("board"):
                # Nếu là lượt đi của đội của mình thì gửi nước đi             
                log_game_info(game_info=game_info)
                if data.get("turn") in self.team_id:
                    self.size = int(data.get("size"))
                    self.board = copy.deepcopy(data.get("board"))


                    # Lấy nước đi từ AI, nước đi là một tuple (i, j)
                    if self.team_roles == Piece.ALLY: # x
                        ai = TicTacToeAI(Piece.ALLY)
                        move = ai.get_move(self.board, self.size)
                        print("Move: ", move)
                    else: # o
                        ai = TicTacToeAI(Piece.ENEMY)
                        move = ai.get_move(self.board, self.size)
                        print("Move: ", move)
                    # Kiểm tra nước đi hợp lệ
                    valid_move = self.check_valid_move(move)
                    # Nếu hợp lệ thì gửi nước đi
                    if valid_move:
                        self.board[int(move[0])][int(move[1])] = self.team_roles
                        game_info["board"] = self.board
                        self.send_move()
                    else:
                        print("Invalid move")
                        
            # Kết thúc trò chơi
            elif data.get("status"):
                print("Game over")
                break

    # Gửi thông tin trò chơi đến server trọng tài
    def send_game_info(self):
        headers = {"Content-Type": "application/json"}
        requests.post(self.server_url, json=game_info, headers=headers)

    def send_move(self):
        # Gửi nước đi đến server trọng tài
        headers = {"Content-Type": "application/json"}
        requests.post(self.server_url + "/move", json=game_info, headers=headers)

    def send_init(self):
        # Gửi yêu cầu kết nối đến server trọng tài
        init_info = {
            "team_id": self.team_id,
            "init": True
        }
        headers = {"Content-Type": "application/json"}
        return requests.post(self.server_url + "/init", json=init_info, headers=headers)

    def fetch_game_info(self):
        # Lấy thông tin trò chơi từ server trọng tài
        request_info = {
            "room_id": self.room_id,
            "team_id": self.team_id,
            "match_id": self.match_id
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.server_url, json=request_info, headers=headers)
        return response

    def check_valid_move(self, new_move_pos):
        # Kiểm tra nước đi hợp lệ
        # Điều kiện đơn giản là ô trống mới có thể đánh vào
        if new_move_pos is None:
            return False
        i, j = int(new_move_pos[0]), int(new_move_pos[1])
        if self.board[i][j] == " ":
            return True
        return False

def log_game_info(game_info):
    # Ghi thông tin trò chơi vào file log
    print("Match id: ", game_info["match_id"])
    print("Room id: ", game_info["room_id"])
    print("Turn: ", game_info["turn"])
    print("Status: ", game_info["status"])
    print("Size: ", game_info["size"])
    print("Board: ")
    for i in range(int(game_info["size"])):
        for j in range(int(game_info["size"])):
            print(f'{game_info["board"][i][j]},', end=" ")
        print()
    print("team1_id:", game_info["team1_id"])
    print("team2_id:", game_info["team2_id"])


# API trả về thông tin trò chơi cho frontend
@app.route('/')
@cross_origin()
def get_data():
    print(game_info)
    response = make_response(jsonify(game_info))
    return response


if __name__ == "__main__":
    # Lấy địa chỉ server trọng tài từ người dùng
    host = input("Enter server url: ")
    team_id = input("Enter team id: ")
    team_roles = input("Enter team role (x/o): ").lower()
    # Khởi tạo game client
    gameClient = GameClient(host, team_id, team_roles)
    game_thread = Thread(target=gameClient.listen)
    game_thread.start()
    app.run(host="0.0.0.0", port=3005)
    try:
        while game_thread.is_alive():
            game_thread.join(1)
    except KeyboardInterrupt:
        stop_thread = True
        game_thread.join()
        print("Game client stopped")
