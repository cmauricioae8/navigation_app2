
"""
@author: C. Mauricio Arteaga-Escamilla

@description: Flet application to manage modes of control for an autonomous mobile robot.

@important: Since it is assumed that octy_bridge2 ROS 2 package is running 
(the Server for both HTTP and SocketIO communications protocols), ROS 2 is NOT required.

The Socket.IO server MUST BE running in order to test this script. ---------
"""

import flet as ft
import time
import requests
from enum import Enum
from components.sio_client_lib import SocketIOClient

SERVER_IP="localhost"
SERVER_PORT="9009"
SIO_EVENT_TIMEOUT = 10.0

# Global instance of our client
sio_client = SocketIOClient(server_url=f'http://{SERVER_IP}:{SERVER_PORT}')

# Http method definition using Enum
class HttpMethod(Enum):
    GET: int = 0
    POST: int = 1

 
class Mode(Enum):
    static: int = 0
    delivery: int = 1 # Should be teleop -----
    mapping: int = 2


current_mode = Mode.static
cancel_transition_mode = False

def show_waiting_view(app_ws_content):
    """
    Function to display the waiting view when transitioning mode.
    'app_ws_content', 'cancel_mode_trans_bt' and 'page' references are required in order to
    modify the 'app_ws_content' by adding vertical elements.
    """
    ## Remember: app_ws_content.controls is a ft.Column
    app_ws_content.controls.clear() #clear all content in app_ws

    app_ws_content.controls.append(
        ft.Text("Please Wait...", size=30, color=ft.Colors.LIGHT_GREEN_ACCENT_700,width=200)
    )
    app_ws_content.controls.append(ft.Container(expand=True))
    app_ws_content.controls.append(
        ft.ProgressRing(
            color=ft.Colors.AMBER_500, bgcolor=ft.Colors.BLUE_GREY,
            width=150, height=150, stroke_width=25)
    )
    app_ws_content.controls.append(ft.Container(expand=True))

def show_teleop_view(app_ws_content):
    app_ws_content.controls.clear() #clear all content in app_ws
    app_ws_content.controls.append(
        ft.Text("Teleoperation Mode", size=30, color=ft.Colors.LIGHT_GREEN_ACCENT_700,width=200)
    )

def try_endpoint(method, url, params, payload) -> list:
    status_code = None
    message = None
    
    try:
        if method == HttpMethod.POST:
            response = requests.post(url, json=payload, params=params, timeout=3)
        elif method == HttpMethod.GET:
            response = requests.get(url, params=params,timeout=3)
        else:
            print(f"Error: {method} NOT supported")
            return False
        
        # response.raise_for_status()
        status_code = response.status_code
        message = response.text

    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return status_code, message

def consume_endpoint(method, expected_code, url_suffix, params, payload):
    url_base = f"http://{SERVER_IP}:{SERVER_PORT}/"
    url = url_base + url_suffix
    # print(f"Change mode: {url=}")

    status_code, message = try_endpoint(method, url, params, payload)

    print(f"{status_code=}\n{message=}")
    
    ## TODO: implement handler exceptions for 3xx and 4xx status codes
    if status_code == expected_code:
        return True
    else: return False


def main(page: ft.Page):
    page.title = "New Navigation App"
    page.bgcolor = ft.Colors.BLUE_GREY_900
    
    ## SocketIO initialization
    sio_client.start()
    time.sleep(0.5)


    ## Cancel mode transition. Alert dialog box ---
    def yes_dlg(e):
        global cancel_transition_mode
        cancel_confirm_dgl.open = False
        cancel_transition_mode = True
        cancel_mode_trans_bt.visible = False
        print("Transition mode canceled!")
        e.control.page.update()
    
    def no_dlg(e):
        cancel_confirm_dgl.open = False
        e.control.page.update()
    
    cancel_confirm_dgl = ft.AlertDialog(
        modal=True, title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to cancel transition?"),
        actions=[
            ft.TextButton("Yes", on_click=yes_dlg),
            ft.TextButton("No", on_click=no_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        # on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    def open_cancel_dlg(e):
        e.control.page.overlay.append(cancel_confirm_dgl)
        cancel_confirm_dgl.open = True
        e.control.page.update()
    
    cancel_mode_trans_bt = ft.ElevatedButton(
        text="Cancel transition", color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_800,
        width=150, height=50, on_click=open_cancel_dlg,
    )
    ## ------


    def validate_changing_mode(e):
        global current_mode, cancel_transition_mode

        desired_mode = Mode(e.control.selected_index)
        print("Selected destination:", desired_mode)

        if current_mode == desired_mode:
            print(f"Already in {current_mode} mode")
            return

        rail.disabled = True
        status_bar.disabled = True
        page.update()

        show_waiting_view(app_ws_content)
        
        # Post method to change mode
        response = consume_endpoint(HttpMethod.POST, 200, "ros/functionality_mode", {}, {"mode": desired_mode.name} )
        
        if response:
            # Due to the http post was success, keep waiting for the SocketIO confirmation
            app_ws_content.controls.append(cancel_mode_trans_bt)
            status_bar_msg.value = "Waiting for robot to be ready ..."
            page.update()

            # Check a change in the function_mode attribute (with timeout to stop waiting)
            if not sio_client.connected:
                status_bar_msg.value = "SocketIO Server NOT available"
                status_bar.bgcolor=ft.Colors.RED_ACCENT_700
                page.update()
                return

            t0 = time.time()
            sio_client.in_waiting = True
            cancel_transition_mode = False
            while(time.time() - t0 < SIO_EVENT_TIMEOUT):
                if sio_client.function_mode == "mau": ## ------------ Modify to test
                    sio_client.in_waiting = False
                    break
                if cancel_transition_mode: # User canceled
                    break
                time.sleep(0.5)
            
            # Verify breaking reason
            if sio_client.in_waiting or not cancel_transition_mode:
                if sio_client.in_waiting:
                    status_bar_msg.value = "Timeout exceed, please try again"
                if cancel_transition_mode:
                    status_bar_msg.value = "Transition mode canceled by the user"
                    page.update()
                app_ws_content.controls.clear()
                ## Endpoint to reset mode (return to static)
                response = consume_endpoint(HttpMethod.POST, 200, "ros/functionality_mode", {}, {"mode":"static"})
                time.sleep(3.0) # Wait for applying changes (not socketio event for this case) ------------------
                response = consume_endpoint(HttpMethod.GET, 200, "ros/functionality_mode", {}, {})
                if response:
                    ## Reset mode variables
                    sio_client.in_waiting = False
                    cancel_transition_mode = False
                    cancel_mode_trans_bt.visible = True
                    print("Reset to static mode success ---------")
                current_mode = Mode.static
                rail.disabled = False
                status_bar.disabled = False
                rail.selected_index = current_mode.value
                page.update()
                return
            else:
                # Continue with the new mode view
                current_mode = desired_mode
                if current_mode == Mode.static:
                    app_ws_content.controls.clear()
                    status_bar_msg.value = "Return to Static Mode"
                elif current_mode == Mode.delivery:
                    show_teleop_view(app_ws_content)
                    status_bar_msg.value = "You can move the robot around"
                else:
                    status_bar_msg.value = f"{str(current_mode)} view NOT implemented yet"
                    app_ws_content.controls.clear() #clear all content in app_ws
                    rail.selected_index = Mode.static.value
        else:
            status_bar.bgcolor = ft.Colors.RED_ACCENT_700
            status_bar_msg.value = "Server NOT available"
            app_ws_content.controls.clear() #clear all content in app_ws
            page.update()
            return

        rail.disabled = False
        status_bar.disabled = False
        page.update()        
    
    
    rail = ft.NavigationRail(
        selected_index=current_mode.value,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100, #scale=1.4,
        bgcolor=ft.Colors.BLUE_200,
        group_alignment=-0.1,
        indicator_color=ft.Colors.RED,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.GPS_NOT_FIXED_ROUNDED,
                selected_icon=ft.Icons.GPS_FIXED_OUTLINED,
                label="Static",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.BOOKMARK_BORDER),
                selected_icon=ft.Icon(ft.Icons.BOOKMARK),
                label="Teleoperation",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MAP_SHARP,
                label_content=ft.Text("Mapping"),
            ),
        ],
        on_change=validate_changing_mode,        
    )

    app_ws_content = ft.Column(
        controls=[
            ft.Text(
                "None Mode Set!", size=40,
                color=ft.Colors.LIGHT_GREEN_ACCENT_700
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    app_ws = ft.Row(
        controls=[
            rail,
            ft.Container(expand=True), #To push rail to left
            app_ws_content,
        ],
        width=700, height=400,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    status_bar_msg = ft.Text("Select a mode to start", size=30, color=ft.Colors.GREY_300)

    status_bar = ft.BottomAppBar(
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,#ft.Colors.LIGHT_BLUE_500,
        content=ft.Row(
            controls=[
                status_bar_msg,
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, 
                              icon_color=ft.Colors.BLACK, scale=1.7),
            ]
        ),
    )
 
    
    ## Add elements to the page
    page.add(status_bar)
    page.add(app_ws)


# --------- Usage -----
if __name__ == "__main__":
    ft.app(target=main)
