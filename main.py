
"""
@author: C. Mauricio Arteaga-Escamilla

@description: Flet application to manage modes of control for an autonomous mobile robot.

@important: Since it is assumed that octy_bridge2 ROS 2 package is running 
(the Server for both HTTP and SocketIO communications protocols), ROS 2 is NOT required.

The Socket.IO server MUST BE running in order to test this script. ---------
"""

import flet as ft
import time
from components.sio_client_lib import SocketIOClient
from utilities.enums import Mode
from config.settings import SERVER_IP, SERVER_PORT
from components.first_comps import rail, app_ws_content, app_ws, status_bar, status_bar_msg
from components.transition_mode_validation import (cancel_mode_trans_bt, cancel_confirm_dgl, 
    yes_bt, no_bt, validate_changing_mode, cancel_mode_yes_dlg)
from components.joystick import joystick, joystick_gd, on_pan_update, on_pan_end


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
                                    app_ws_content, status_bar_msg, sio_client, joystick)
    
    
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
    

    ## Add elements to the page
    page.add(status_bar)
    page.add(app_ws)
    page.add(ft.Container(expand=True))

    #joystick MUST be directly in the page
    page.add( ft.Row(controls=[ joystick ]) )


# --------- Usage -----
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
