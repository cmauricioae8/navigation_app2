
import flet as ft


def show_waiting_view(app_ws_content):
    """
    Function to display the waiting view when transitioning mode.
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

