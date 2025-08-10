
"""
@author: C. Mauricio Arteaga-Escamilla

@description: Flet application to manage modes of control for an autonomous mobile robot.

@important: Since it is assumed that octy_bridge2 ROS 2 package is running 
(Server for both HTTP and SocketIO communications methods), ROS 2 is NOT required.
"""

import flet as ft


def main(page: ft.Page):
    page.title = "New Navigation App"
    page.bgcolor = ft.Colors.BLUE_GREY_900


    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
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
        on_change=lambda e: print(f"{e.control.selected_index} index chosen"),        
    )

    app_ws = ft.Row(
        controls=[
            rail,
            ft.Column(
                controls=[
                    ft.Text(
                        "None Mode Set!", size=40,
                        color=ft.Colors.LIGHT_GREEN_ACCENT_700
                    ),
                ],
                alignment=ft.MainAxisAlignment.START, expand=True
            ),
        ],
        width=700, height=400,
    )

    status_bar = ft.BottomAppBar(
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,#ft.Colors.LIGHT_BLUE_500,
        content=ft.Row(
            controls=[
                ft.Text("Select a mode to start", size=30, color=ft.Colors.GREY_300),
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
