
"""
@author: C. Mauricio Arteaga-Escamilla

@description: Flet application to manage modes of control for an autonomous mobile robot.

@important: Since it is assumed that octy_bridge2 ROS 2 package is running 
(the Server for both HTTP and SocketIO communications protocols), ROS 2 is NOT required.

The Socket.IO server MUST BE running in order to test this script. ---------
"""

import flet as ft
import time, threading
from components.sio_client_lib import SocketIOClient
from utilities.enums import Mode
from config.settings import SERVER_IP, SERVER_PORT
from components.first_comps import rail, app_ws_content, app_ws, status_bar, status_bar_msg, interactive_viewer
from components.transition_mode_validation import (cancel_mode_trans_bt, cancel_confirm_dgl, 
    yes_bt, no_bt, validate_changing_mode, cancel_mode_yes_dlg)
from components.joystick import joystick, joystick_gd, on_pan_update, on_pan_end
import base64, os


def main(page: ft.Page):
    page.title = "New Navigation App"
    page.bgcolor = ft.Colors.BLUE_GREY_900

    cancel_transition_mode = False
    current_mode = Mode.static
    sio_client = SocketIOClient(server_url=f'http://{SERVER_IP}:{SERVER_PORT}')

    ## SocketIO initialization
    sio_client.start()
    time.sleep(0.5)


    ## Cancel mode transition. Alert dialog box ---
    def cancel_mode_yes_dlg_wrap(e):
        cancel_mode_yes_dlg(e, cancel_confirm_dgl, cancel_transition_mode, cancel_mode_trans_bt)
    
    def cancel_mode_no_dlg(e):
        cancel_confirm_dgl.open = False
        e.control.page.update()
    
    yes_bt.on_click=cancel_mode_yes_dlg_wrap
    no_bt.on_click=cancel_mode_no_dlg

    def open_cancel_dlg(e):
        e.control.page.overlay.append(cancel_confirm_dgl)
        cancel_confirm_dgl.open = True
        e.control.page.update()
    
    cancel_mode_trans_bt.on_click = open_cancel_dlg
    ## ------


    def validate_changing_mode_wrap(e):
        desired_mode = Mode(e.control.selected_index).name
        validate_changing_mode(current_mode, cancel_transition_mode, desired_mode, rail, status_bar, page,
                                    app_ws_content, status_bar_msg, sio_client, joystick, app_ws)
    
    
    rail.on_change = validate_changing_mode_wrap

    
    ## Joystick drag update function
    def on_pan_update_wrap(e: ft.DragUpdateEvent):
        on_pan_update(e, sio_client)
        
    def on_pan_end_wrap(e: ft.DragEndEvent):
        on_pan_end(e, sio_client)  

    joystick_gd.on_vertical_drag_update = on_pan_update_wrap
    joystick_gd.on_horizontal_drag_update = on_pan_update_wrap
    joystick_gd.on_vertical_drag_end = on_pan_end_wrap
    joystick_gd.on_horizontal_drag_end = on_pan_end_wrap
    
    # map_img =ft.Image(src="/home/mau/icon.png", width=800)

    # Periodic watcher
    def periodic_function():
        print("Periodic function stared ------")
        i = 0
        while True:
            if sio_client.connected:
                map_event = sio_client.map_dict
                if map_event is not None and isinstance(map_event, dict):
                    page.update()
                    print("Receiving map!!!")

                    img_base64_str = map_event['image'].removeprefix("data:image/png;base64,")
                    image_data = base64.b64decode(img_base64_str) #.decode('utf-8')
                    
                    i = i+1                    
                    map_output_filename = "map_temp"+str(i)+".png"
                    with open(map_output_filename, "wb") as f:
                        f.write(image_data)
                        print("*** Image temp map updated")

                    time.sleep(0.5)
                    app_ws.controls[3].content.src = map_output_filename

                    page.update()
                    app_ws.controls[3].update()
                    sio_client.map_dict = None
            
                time.sleep(0.2)

    th = threading.Thread(target=periodic_function) #daemon=True
    th.daemon = True
    th.start()

    ## Add elements to the page
    page.add(status_bar)
    page.add(app_ws)
    # page.add(map_img)
    page.add(ft.Container(expand=True))

    #joystick MUST be directly in the page
    page.add( ft.Row(controls=[ joystick ]) )


# --------- Usage -----
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
