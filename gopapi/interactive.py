from __future__ import absolute_import
from gopapi.api import API
import curses
import curses.textpad
import json


scr = curses.initscr()
curses.noecho()
max_y, max_x = scr.getmaxyx()

api = API.shared()

# Main menu
scr.addstr(1, 0, 'd - Domains')
c = scr.getch()

def draw_field(scr, y, x, size=40, label='Field'):
    scr.addstr(y, x + 3, label)
    curses.textpad.rectangle(scr, y + 1, x, y + 3, x + size)

def input_text(scr, y, x, **kwargs):
    draw_field(scr, y, x, **kwargs)
    curses.echo()
    s = scr.getstr(y + 2, x + 3)
    curses.noecho()
    return s

if c == ord('d') or c == ord('D'):
    scr.addstr(1, 0, 'l - List all domains')
    scr.addstr(2, 0, 'a - Add record')
    scr.addstr(3, 0, 'i - Domain info')
    scr.addstr(4, 0, 'Ctrl-C to go back')
    
    c = scr.getch()

    if c == ord('l') or c == ord('L'):
        response = api.get('/domains')
        domains = response.json()
        for index, d in enumerate(domains):
            try:
                scr.addstr(index + 1, 2, d['domain'])
            except:
                break
        scr.getch()

    if c == ord('i') or c == ord('I'):
        scr.addstr(6, 1, 'Which domain?')
        curses.echo()
        curses.textpad.rectangle(scr, 7, 1, 9, 40)
        curses.setsyx(10, 10)
        try:
            domain_name = scr.getstr(8, 3).decode('utf-8')
            scr.clear()
            scr.addstr(0, 0, 'Domain: {}'.format(domain_name))
            scr.addstr(max_y - 1, 1, 'Ctrl-C to go back')
            curses.noecho()

            scr.addstr(1, 0, 'Downloading...')
            scr.refresh()

            response = api.get('/domains/{}'.format(domain_name))
            if response.status_code == 200:
                info = response.json()
                scr.addstr(1, 0, ' ' * max_x)
                scr.addstr(2, 1, 'Status: {}'.format(info['status']))
                scr.addstr(3, 1, 'Expires: {}'.format(info['expires']))
                
                # Menu del dominio
                scr.addstr(4, 1, 'a - Add register')

                c = scr.getch()

                # TODO: make a function in API class for adding
                #       the register, so it can be called from cli
                #       and interactive mode same way.
                if c == ord('a') or c == ord('A'):
                    scr.addstr(8, 1, 'Type (a, mx, cname, aaaa)')
                    curses.textpad.rectangle(scr, 9, 1, 11, 25)
                    curses.echo()
                    rectype = scr.getstr(10, 3)
                    curses.noecho()

                    scr.addstr(12, 1, 'Subdomain')
                    curses.textpad.rectangle(scr, 13, 1, 15, 40)
                    curses.echo()
                    subdomain = scr.getstr(14, 3)
                    curses.noecho()

                    if rectype == b'a':
                        scr.addstr(16, 1, 'IPv4 address')
                        curses.textpad.rectangle(scr, 17, 1, 19, 40)
                        curses.echo()
                        ip = scr.getstr(18, 3)
                        curses.noecho()

                    elif rectype == b'cname':
                        target_doman = input_text(scr, 17, 1,
                            size=40,
                            label='Target domain')

                    curses.textpad.rectangle(scr, 20, 1, 22, 16)
                    curses.textpad.rectangle(scr, 20, 22, 22, 38)
                    scr.addstr(21, 3, 'Create (Y)')
                    scr.addstr(21, 24, 'Do not (N)')

                    c = scr.getch()

                    if c == ord('y') or c == ord('Y'):
                        """url = 'domains/{}/records'.format(domain_name)
                        params = [
                            {
                                'type': args.data[0].upper(), # A / CNAME
                                'name': args.data[1], # fulano., mangano.
                                'data': args.data[2], # points to ip/domain
                            }
                        ]"""
                        pass

                scr.refresh()
            else:
                scr.addstr(1, 0, "Domain doesn't exist or it's not yours.")

            scr.getch()

        except KeyboardInterrupt:
            pass

curses.endwin()
