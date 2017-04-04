#!/usr/bin/env python

import webmapper_http_server as server
import mapper
import mapperstorage
import netifaces # a library to find available network interfaces
import sys, os, os.path, threading, json, re, pdb
from random import randint

networkInterfaces = {'active': '', 'available': []}

dirname = os.path.dirname(__file__)
if dirname:
   os.chdir(os.path.dirname(__file__))

if 'tracing' in sys.argv[1:]:
    server.tracing = True

def open_gui(port):

    url = 'http://localhost:%d'%port
    apps = ['~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe --app=%s',
            '/usr/bin/chromium-browser --app=%s',
            ]
    if 'darwin' in sys.platform:
        # Dangerous to run 'open' on platforms other than OS X, so
        # check for OS explicitly in this case.
        apps = ['open -n -a "Google Chrome" --args --app=%s']
    def launch():
        try:
            import webbrowser, time
            time.sleep(0.2)
            for a in apps:
                a = os.path.expanduser(a)
                a = a.replace('\\','\\\\')
                if webbrowser.get(a).open(url):
                    return
            webbrowser.open(url)
        except:
            print 'Error opening web browser, continuing anyway.'
    launcher = threading.Thread(target=launch)
    launcher.start()

monitor = mapper.database(subscribe_flags=mapper.OBJ_DEVICES | mapper.OBJ_LINKS)
#monitor = mapper.monitor(autosubscribe_flags=mapper.SUB_DEVICE | mapper.SUB_DEVICE_LINKS_OUT)

def on_device(dev, action):
    if action == mapper.ADDED:
        print "Device " + dev.name + "added"
        props = dev.properties.copy()
        props['synced'] = props['synced'].get_double()
        server.send_command("new_device", props)
    if action == mapper.MODIFIED:
        print "Device ", dev.name, "modified"
        props = dev.properties.copy()
        props['synced'] = props['synced'].get_double()
        server.send_command("new_device", props)
    if action == mapper.REMOVED:
        print "Device ", dev.name, "removed"
        props = dev.properties.copy()
        props['synced'] = props['synced'].get_double()
        server.send_command("new_device", props)

def on_signal(sig, action):
    if action == mapper.ADDED:
        props = sig.properties.copy()
        props["device_name"] = sig.device().name
        props["name"] = "/" + props["name"]
        server.send_command("new_signal", props)
    if action == mapper.MODIFIED:
        props = sig.properties.copy()
        props["device_name"] = sig.device().name
        #props["name"] = "/" + props["name"]
        server.send_command("mod_signal", props)
    if action == mapper.REMOVED:
        props = sig.properties.copy()
        props["device_name"] = sig.device().name
        server.send_command("del_signal", props)

def on_link(link, action):
    if action == mapper.ADDED:
        print type(link)
        props = link.properties.copy()
        props["src_name"] = link.device(1).name
        props["dest_name"] = link.device(0).name
        print "Link added from " + props["src_name"] + " to " + props["dest_name"]
        server.send_command("new_link", props)
    if action == mapper.MODIFIED:
        print "Link modified"
        props = link.properties.copy()
        server.send_command("mod_link", props)
    if action == mapper.REMOVED:
        print "Link removed"
        props = link.properties.copy()
        server.send_command("del_link", props)

#TODO: rename to on_map for 1.0
def on_connection(con, action):
    if action == mapper.ADDED:
        print "Connection added"
        props = con.properties.copy()
        server.send_command("new_connection", props)
    if action == mapper.MODIFIED:
        print "Connection modified"
        props = con.properties.copy()
        server.send_command("new_connection", props)
    if action == mapper.REMOVED:
        print "Connection removed"
        props = con.properties.copy()
        server.send_command("new_connection", props)

#TODO: rename to set_map for 1.0
def set_connection(con):
    if con.has_key('mode'):
        con['mode'] = {'bypass': mapper.BOUND_NONE,
                       'reverse': mapper.BOUND_FOLD, #fold == reverse??
                       'linear': mapper.MODE_LINEAR,
                       'calibrate': mapper.MO_CALIBRATE, #?!
                       'expression': mapper.MODE_EXPRESSION}[con['mode']]
    if (con.has_key('src_min')):
        if (type(con['src_min']) is int or type(con['src_min']) is float):
            con['src_min'] = float(con['src_min'])
            numargs = 1
        else:
            if (type(con['src_min']) is str):
                con['src_min'] = con['src_min'].replace(',',' ').split()
            numargs = len(con['src_min'])
            for i in range(numargs):
                con['src_min'][i] = float(con['src_min'][i])
            if numargs == 1:
                con['src_min'] = con['src_min'][0]
        con['src_type'] = 'f'
    if (con.has_key('src_max')):
        if (type(con['src_max']) is int or type(con['src_max']) is float):
            con['src_max'] = float(con['src_max'])
            numargs = 1;
        else:
            if (type(con['src_max']) is str):
                con['src_max'] = con['src_max'].replace(',',' ').split()
            numargs = len(con['src_max'])
            for i in range(numargs):
                con['src_max'][i] = float(con['src_max'][i])
            if numargs == 1:
                con['src_max'] = con['src_max'][0]
        con['src_type'] = 'f'
    if (con.has_key('dest_min')):
        if (type(con['dest_min']) is int or type(con['dest_min']) is float):
            con['dest_min'] = float(con['dest_min'])
            numargs = 1;
        else:
            if (type(con['dest_min']) is str):
                con['dest_min'] = con['dest_min'].replace(',',' ').split()
            numargs = len(con['dest_min'])
            for i in range(numargs):
                con['dest_min'][i] = float(con['dest_min'][i])
            if numargs == 1:
                con['dest_min'] = con['dest_min'][0]
        con['src_type'] = 'f'
    if (con.has_key('dest_max')):


        if (type(con['dest_max']) is int or type(con['dest_max']) is float):
            con['dest_max'] = float(con['dest_max'])
            numargs = 1;
        else:
            if (type(con['dest_max']) is str):
                con['dest_max'] = con['dest_max'].replace(',',' ').split()
            numargs = len(con['dest_max'])
            for i in range(numargs):
                con['dest_max'][i] = float(con['dest_max'][i])
            if numargs == 1:
                con['dest_max'] = con['dest_max'][0]
        con['src_type'] = 'f'
    monitor.modify_connection(con['src_name'], con['dest_name'], con)
    

def on_refresh(arg):
    global monitor
    del monitor
    admin = mapper.network(networkInterfaces['active'])
    monitor = mapper.database(admin, autosubscribe_flags=mapper.OBJ_DEVICES | mapper.OBJ_OUTPUT_SIGNALS)
    init_monitor()

def on_save(arg):
    ds = list(monitor.mapper_database_devices_by_name(arg['dev']))
    fn = '/'.join(ds[0]['name'].split('/')[1:])
    fn.replace('/','_')
    fn = '.'.join(fn.split('.')[:-1]+['json'])
    return fn, mapperstorage.serialise(monitor, arg['dev'])

def on_load(mapping_json, devices):
    # pdb.set_trace()
    mapperstorage.deserialise(monitor, mapping_json, devices)

def select_network(newNetwork):
    # print 'select_network', newNetwork
    networkInterfaces['active'] = newNetwork
    server.send_command('set_network', newNetwork)

def get_networks(arg):
    location = netifaces.AF_INET    # A computer specific integer for internet addresses
    totalInterfaces = netifaces.interfaces() # A list of all possible interfaces
    connectedInterfaces = []
    for i in totalInterfaces:
        addrs = netifaces.ifaddresses(i)
        if location in addrs:       # Test to see if the interface is actually connected
            connectedInterfaces.append(i)
    server.send_command("available_networks", connectedInterfaces)
    networkInterfaces['available'] = connectedInterfaces
    server.send_command("active_network", networkInterfaces['active'])

def get_active_network(arg):
    print networkInterfaces['active']
    server.send_command("active_network", networkInterfaces['active'])


def init_monitor():
    monitor.add_device_callback(on_device)
    monitor.add_signal_callback(on_signal)
    monitor.add_link_callback(on_link)
    #monitor.add_map_callback(on_connection) # "connection" from 0.4 is now a "map" in 1.0

init_monitor()

server.add_command_handler("all_devices",
                           lambda x: ("all_devices",
                                      list(monitor.devices())))

def select_tab(src_dev):
    # TODO:
    # if src_dev != focus_dev and focus_dev != "All Devices":
    #     # revert device subscription back to only device and link metadata
    #     monitor.subscribe(focus_dev, mapper.SUB_DEVICE | mapper.SUB_DEVICE_LINKS_OUT, -1)
    if src_dev != "All Devices":
        dev = monitor.device(src_dev)
        monitor.subscribe(dev, mapper.OBJ_OUTPUT_SIGNALS | mapper.OBJ_MAPS, -1)
        # 0.4 -> 1.0 changes:
        links = dev.links()
        print "num links = ", dev.num_links
        count = 1
        for i in links:
            #monitor.subscribe(i["dest_name"], mapper.SUB_DEVICE_INPUTS, -1)
            # linkprops = i.properties.copy() #no need to copy props for now
            # print str(count) + str(linkprops['num_maps'])
            linkdev = i.device(0)
            if linkdev.id != i.id:
                #subscribe to inputs
                monitor.subscribe(linkdev, mapper.OBJ_INPUT_SIGNALS)

            linkdev = i.device(1)
            if linkdev.id != i.id:
                #subscribe to inputs
                monitor.subscribe(linkdev, mapper.OBJ_INPUT_SIGNALS)

            count=count+1

            #print i["dest_name"]
            #monitor.subscribe(i["dest_name"], mapper.OBJ_INCOMING_MAPS, -1)

#TODO: rename to new_map for 1.0
def new_connection(args):
    source = str(args[0])
    dest = str(args[1])
    options = {}
    if( len(args) > 2 ): # See if the connection message has been supplied with options
        if( type(args[2]) is dict ): # Make sure they are the proper format
            options = args[2]
    monitor.connect(source, dest, options)

server.add_command_handler("tab", lambda x: select_tab(x))

server.add_command_handler("all_signals",
                           lambda x: ("all_signals", list(monitor.signals()))) # .db.all_inputs())
                                       # + list(monitor.db.all_outputs())))

server.add_command_handler("all_links",
                           lambda x: ("all_links", list(monitor.links()))) # .db.all_links())))

#TODO: rename to maps for 1.0, sync in main.js
server.add_command_handler("all_connections",
                           lambda x: ("all_connections",
                                      list(monitor.maps())))
#TODO: rename to maps for 1.0, sync in main.js
server.add_command_handler("set_connection", set_connection)

server.add_command_handler("link",
                           lambda x: monitor.link(*map(str,x)))

server.add_command_handler("unlink",
                           lambda x: monitor.unlink(*map(str,x)))
#TODO: rename to map for 1.0, sync in main.js
server.add_command_handler("connect", lambda x: new_connection(x))

#TODO: rename to unmap for 1.0, sync in main.js
server.add_command_handler("disconnect",
                           lambda x: monitor.disconnect(*map(str,x)))

server.add_command_handler("refresh", on_refresh)

server.add_command_handler("save", on_save)
server.add_command_handler("load", on_load)

server.add_command_handler("select_network", select_network)
server.add_command_handler("get_networks", get_networks)

get_networks(False)
if ( 'en1' in networkInterfaces['available'] ) :
    networkInterfaces['active'] = 'en1'
elif ( 'en0' in networkInterfaces['available'] ):
    networkInterfaces['active'] = 'en0'
elif ( 'lo0' in networkInterfaces['available'] ):
    networkInterfaces['active'] = 'lo0'

try:
    port = int(sys.argv[sys.argv.index('--port'):][1])
except:
    #port = randint(49152,65535)
    port = 50000

on_open = lambda: ()
if not '--no-browser' in sys.argv and not '-n' in sys.argv:
    on_open = lambda: open_gui(port)



server.serve(port=port, poll=lambda: monitor.poll(100), on_open=on_open,
             quit_on_disconnect=not '--stay-alive' in sys.argv)

