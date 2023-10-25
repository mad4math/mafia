from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import io
import time
import urllib
import get_games
import load_player
import load_admin
import generate_game
import update_player
import save_admin
import sys
import mafia
import os



class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path[1:]
        out = io.TextIOWrapper(self.wfile)
        d = urllib.parse.parse_qs(url.query)
        if path == "get-games":
            response = get_games.get_games()
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            out.write(response)
        elif path == "generate-game":
            generate_game.generate_game(d)
            response = """<meta http-equiv="Refresh" content="0; url='admin.html'" />"""
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            out.write(response)
        elif path == "load-player":
            response = load_player.load_player(d)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            out.write(response)
        elif path == "load-admin":
            response = load_admin.load_admin(d)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            out.write(response)
        else:
            super().do_GET()
        out.detach()
    
    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path[1:]
        out = io.TextIOWrapper(self.wfile)
        d = urllib.parse.parse_qs(str(self.rfile.read(int(self.headers["Content-Length"])), "utf-8"))
        if path == "update-player":
            response = update_player.update_player(d)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
        elif path == "save-admin":
            response = save_admin.save_admin(d)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
        else:
            self.send_response(200)
            response = "bad post request"
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        out.write(response)
        out.detach()




if __name__ == "__main__":
    if not os.path.isfile('config.ini'):
        with open('config.ini','w') as file:
            file.write('mafia-games/')
    if not os.path.exists(mafia.get_game_file_location(None)):
        os.mkdir(mafia.get_game_file_location(None))
    if len(sys.argv) > 1:
        hostName = sys.argv[1]
    else:
        hostName = "localhost"
    if len(sys.argv) > 2:
        serverPort = int(sys.argv[2])
    else:
        serverPort = 8080
    print(sys.argv)
    webServer = ThreadingHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")