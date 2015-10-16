'''
Created on Oct 16, 2015

@author: casey
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import sqlite3, urlparse
import os, sys
import csv
import tabulate

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        qs = []
        path = self.path
        if '?' in path:
            path, tmp = path.split('?', 1)
            qs.append(urlparse.parse_qs(tmp))
        
        for var in qs:
            if 'query' in var:
                try:
                    result, headers = self.execute_query(var['query'][0])
                    if result is not None:
                        if len(result) > 0:
                            self.wfile.write(tabulate.tabulate(result[:100], headers, tablefmt="html").encode("ascii", "xmlcharrefreplace"))
                            return                    
                except Exception as detail:
                    self.wfile.write(detail)
                return
            
        
        
        self.wfile.write("empty result set")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        
    def startdb(self):
        return sqlite3.connect('take.db')
        
    def closedb(self, conn):
        conn.commit()
        conn.close()    
        
    def execute_query(self, query):
        conn = self.startdb()
        c = conn.cursor()
        handle = c.execute(query)
        names = ['row'] + [m for m in map(lambda x: x[0], handle.description)]
        handles = [row for row in handle]        
        results = []
        i = 1
        for handle in handles:
            result = [i]
            for col_name,value in zip(names,handle): 
                result.append(value)
            results.append(result)
            i += 1
        self.closedb(conn)
        return results, names
        
def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()