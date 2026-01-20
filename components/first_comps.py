
import flet as ft

# NavigationRail to define different modes of operation
rail = ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=100, #scale=1.4,
    height=400,
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
    ], #on_change=validate_changing_mode,
)

# Content area for the application workspace
# This will change based on the selected mode in the NavigationRail
app_ws_content = ft.Column(
    controls=[
        ft.Text(
            "None Mode Set!", size=40,
            color=ft.Colors.LIGHT_GREEN_ACCENT_700
        ),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)

interactive_viewer = ft.InteractiveViewer(
    min_scale=0.6,
    max_scale=5,
    boundary_margin=ft.margin.all(20),
    # on_interaction_start=lambda e: print(e),
    # on_interaction_end=lambda e: print(e),
    # on_interaction_update=lambda e: print(e),
    content=ft.Image(src="/home/mau/icon.png"),
    width=1200,
    height=1200,
    # visible=True,
)

# Main application workspace combining the NavigationRail and content area
app_ws = ft.Row(
    controls=[
        rail,
        ft.Container(expand=True), #To push rail to left
        app_ws_content,
        interactive_viewer,
    ],
    width=700, height=400,
    alignment=ft.MainAxisAlignment.CENTER,
)

# Status bar to display messages and settings icon
# This will show the current status or instructions to the user
status_bar_msg = ft.Text("Select a mode to start", size=30, color=ft.Colors.GREY_300)

# BottomAppBar to hold the status message and settings icon
# The status bar will be at the bottom of the application window
status_bar = ft.BottomAppBar(
    bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
    content=ft.Row(
        controls=[
            status_bar_msg,
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=ft.Colors.BLACK, scale=1.7),
        ],
    ),
    height=70,
)

# Interactive viewer for maps
# interactive_viewer = ft.Row(
#     [
#         ft.InteractiveViewer(
#             min_scale=0.4,
#             max_scale=10,
#             boundary_margin=ft.margin.all(20),
#             # on_interaction_start=lambda e: print(e),
#             # on_interaction_end=lambda e: print(e),
#             # on_interaction_update=lambda e: print(e),
#             content=ft.Image(src="assets/joystick.png"),
#             width=600,
#             height=600,
#         )
#     ]
# )

