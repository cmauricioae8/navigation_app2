
import flet as ft
import time
from components.show_views import show_waiting_view, show_teleop_view
from utilities.functions import consume_endpoint, HttpMethod
from config.settings import SIO_EVENT_TIMEOUT
from utilities.enums import Mode


## Cancel mode transition. Alert dialog box ---
yes_bt = ft.TextButton("Yes")
no_bt = ft.TextButton("No")

def cancel_mode_yes_dlg(e, cancel_confirm_dgl, cancel_transition_mode, cancel_mode_trans_bt):
    cancel_confirm_dgl.open = False
    cancel_transition_mode = True
    cancel_mode_trans_bt.visible = False
    print("Transition mode canceled!")
    e.control.page.update()


cancel_confirm_dgl = ft.AlertDialog(
    modal=True, title=ft.Text("Please confirm"),
    content=ft.Text("Do you really want to cancel transition?"),
    actions=[
        yes_bt,
        no_bt,
    ],
    actions_alignment=ft.MainAxisAlignment.END,
)

cancel_mode_trans_bt = ft.ElevatedButton(
    text="Cancel transition", color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_800,
    width=160, height=50, #on_click=open_cancel_dlg,
)
## ------


def validate_changing_mode(current_mode, cancel_transition_mode, desired_mode, rail, status_bar, page, app_ws_content,
                                status_bar_msg, sio_client, joystick):
    """
    Validate and change the robot's mode. Endpoints are consumed to change the mode and wait for confirmation via SocketIO.
    If the mode change is successful, the appropriate view is displayed based on the new mode.
    If the mode change fails or is canceled, the system reverts to static mode and updates the UI accordingly.
    """

    print("Selected destination:", desired_mode)

    if current_mode == desired_mode:
        print(f"Already in {current_mode} mode")
        return

    rail.disabled = True
    status_bar.disabled = True
    page.update()

    show_waiting_view(app_ws_content)

    # Post method to change mode
    response = consume_endpoint(HttpMethod.POST, 200, "ros/functionality_mode", {}, {"mode": desired_mode} )
        
    if response:
        # Due to the http post was success, keep waiting for the SocketIO confirmation
        if desired_mode != Mode.static.name: app_ws_content.controls.append(cancel_mode_trans_bt)
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
        print(f"Waiting for transition...\n")

        while(time.time() - t0 < SIO_EVENT_TIMEOUT):
            if sio_client.function_mode == desired_mode: ## ------------ Modify to test
                sio_client.in_waiting = False
                print(f"New mode: {desired_mode} success")
                break
            if cancel_transition_mode: # User canceled
                break
            time.sleep(0.5)
        
        # Verify breaking reason
        if sio_client.in_waiting or cancel_transition_mode:
            if sio_client.in_waiting:
                status_bar_msg.value = "Timeout exceed, please try again"
            elif cancel_transition_mode:
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
            if current_mode == Mode.static.name:
                app_ws_content.controls.clear()
                status_bar_msg.value = "Return to Static Mode"
                joystick.visible = False
            elif current_mode == Mode.delivery.name:
                show_teleop_view(app_ws_content)
                status_bar_msg.value = "You can move the robot around"
                joystick.visible = True

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