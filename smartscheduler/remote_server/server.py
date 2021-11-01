from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import csv
import json
import sqlite3


class HandleRequests(BaseHTTPRequestHandler):

    @staticmethod
    def __db_cmd__(cmd: str, params: list, exc_many: bool) -> tuple:
        conn = None
        db_err = False
        db_ret = ""
        try:
            conn = sqlite3.connect("./SmartScheduler.db")
            curs = conn.cursor()
            if exc_many:
                curs.executemany(cmd, params)
            else:
                curs.execute(cmd, params) if params is not None else curs.execute(cmd)
        except (sqlite3.IntegrityError, sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            db_err = True
            db_ret = e.args[0]
        else:
            conn.commit()
            db_ret = curs.fetchall()
        finally:
            if conn:
                conn.close()
            return db_ret, db_err

    @staticmethod
    def __upd_sub_list__(upd_cmd: str):
        db_ret, db_err = "", False
        try:
            with open("./subjects.csv") as sub_f:
                reader = csv.DictReader(sub_f)
                sub_info = [(sub["sub_code"], sub["sub_name"]) for sub in reader]
        except csv.Error:
            db_err = True
            db_ret = "Subjects info file corrupted."
        except FileNotFoundError:
            db_err = True
            db_ret = "Subjects info file not found."
        else:
            db_ret, db_err = HandleRequests.__db_cmd__(upd_cmd, sub_info, exc_many=True)
        finally:
            return db_ret, db_err

    def send_success_response(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self.send_response(501)
        self.end_headers()

    def do_POST(self):
        if self.headers["Content-Type"] != "application/json":
            self.send_response(400)
            return self.end_headers()
        alen: int = int(self.headers["Content-Length"])
        args: dict = json.loads(self.rfile.read(alen))
        cmd: str = args.get("cmd", "")
        cmd_params: list = args.get("cmd_params", None)
        print(f"SQL cmd: {cmd}\n params: {cmd_params}")
        if cmd_params and cmd_params[0] == "upd_subs":
            db_resp: tuple = self.__upd_sub_list__(cmd)
        else:
            db_resp: tuple = self.__db_cmd__(cmd, cmd_params, False)
        self.send_success_response()
        self.wfile.write(json.dumps({"db_ret": db_resp[0], "db_err": db_resp[1]}).encode("utf-8"))

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), HandleRequests)
    try:
        print("Server started.")
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
        print("Server terminated by Ctrl + C.")
