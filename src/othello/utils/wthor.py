import os
import csv


CODING = "iso-8859-2"

class Wthor:
    def __init__(self, wtb, jou, trn):
        self.players = self.get_file_data(jou, 20)
        self.tournaments = self.get_file_data(trn, 26)
        self.game_datas = self.get_game_data(wtb)

    def get_game_data(self, filepath):
        data = []
        with open(filepath, "rb") as file:
            header = self.get_header(file)
            for _ in range(header["game_count"]):
                data.append({
                    "game_year": header["game_year"],
                    "tournament": self.tournaments[int.from_bytes(file.read(2), "little")],
                    "black_player": self.players[int.from_bytes(file.read(2), "little")],
                    "white_player": self.players[int.from_bytes(file.read(2), "little")],
                    "black_score": int.from_bytes(file.read(1), "little"),
                    "depth": header["depth"],
                    "theoretical_score": int.from_bytes(file.read(1), "little"),
                    "record": self.get_recode(file)
                })
        return data
    
    def get_file_data(self, filepath, byte):
        data = []
        with open(filepath, "rb") as file:
            header = self.get_header(file)
            for _ in range(header["records"]):
                data.append(file.read(byte).decode(CODING).replace("\x00", ""))
        return data
    
    def get_header(self, file):
        return {
            "created_date": self.create_date(file),
            "game_count": int.from_bytes(file.read(4), byteorder="little"),
            "records": int.from_bytes(file.read(2), byteorder="little"),
            "game_year": int.from_bytes(file.read(2), byteorder="little"),
            "size": int.from_bytes(file.read(1), byteorder="little"),
            "type": int.from_bytes(file.read(1), byteorder="little"),
            "depth": int.from_bytes(file.read(1), byteorder="little"),
            "spare": int.from_bytes(file.read(1), byteorder="little"),
        }
    
    def create_date(self, file):
        year = str(int.from_bytes(file.read(1), byteorder="little")) + str(int.from_bytes(file.read(1), byteorder="little"))
        month = str(int.from_bytes(file.read(1), byteorder="little"))
        day = str(int.from_bytes(file.read(1), byteorder="little"))
        return f"{year}/{month}/{day}"
    
    def get_recode(self, file):
        recode = ""
        for _ in range(60):
            pos = int.from_bytes(file.read(1), "little")
            if pos:
                pos = str(pos)
                recode += chr(ord("a") + int(pos[1]) - 1) + pos[0]
        return recode
    
    def to_csv(self, filename, mode="w"):
        header = ["game_year", "tournament", "black_player", "white_player", "black_score", "depth", "theoretical_score", "record"]
        with open(filename, mode, newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, header)
            writer.writeheader()
            writer.writerows(self.game_datas)
    
#if __name__ == "__main__":
    # load_folder_path = "wthor"
    # add_folder_path = "wthor_csv"
    # files = os.listdir(load_folder_path)
    # jou = os.path.join(load_folder_path, files[0])
    # trn = os.path.join(load_folder_path, files[1])
    # for wtb in files[2:]:
    #     print(wtb, end=" ")
    #     try:
    #         wthor = Wthor(os.path.join(load_folder_path, wtb), jou, trn)
    #         filename = os.path.splitext(wtb)[0] + ".csv"
    #         wthor.to_csv(os.path.join(add_folder_path, filename))
    #         print("success")
    #     except ValueError as e:
    #         print(e)
    