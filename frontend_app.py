# frontend_app.py
import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Secure Library Network"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 20

    # --- MEMORY STABLE CONTROLLERS (Re-used fields to prevent memory clutter) ---
    lib_email = ft.TextField(label="Staff Email ID", prefix_icon=ft.Icons.EMAIL_OUTLINED, border_radius=8)
    lib_pass = ft.TextField(label="Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINED, border_radius=8)
    
    student_id = ft.TextField(label="Roll Number or Mobile Number", prefix_icon=ft.Icons.CONTACTS_OUTLINED, border_radius=8, hint_text="e.g. GUVIDS1234 or 9876543210")
    student_otp = ft.TextField(label="Enter 6-Digit OTP", prefix_icon=ft.Icons.PASSWORD, border_radius=8, visible=False, text_align=ft.TextAlign.CENTER)

    action_button = ft.Button(
        content="Request Verification OTP",
        bgcolor=ft.Colors.DEEP_PURPLE,
        color=ft.Colors.WHITE,
        height=45,
        width=320,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # --- CARD NAVIGATION ENGINE ---
    def switch_tab(e):
        selected_role = e.control.selected[0]
        
        if selected_role == "student":
            librarian_form.visible = False
            student_form.visible = True
            action_button.content = "Request Verification OTP"
            action_button.on_click = trigger_student_otp_request
        else:
            student_form.visible = False
            librarian_form.visible = True
            action_button.content = "Verify Staff Login"
            action_button.on_click = trigger_librarian_login
        page.update()

    # --- LIVE BACKEND NETWORK LINK MECHANICS ---
    BACKEND_URL = "http://127.0.0.1:8000"

    def trigger_librarian_login(e):
        payload = {
            "email": lib_email.value.strip(),
            "password": lib_pass.value.strip()
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login/librarian", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                page.session.store.set("token", data["access_token"])
                page.session.store.set("role", data["role"])
                page.session.store.set("name", data["name"])
                
                show_success_toast(f"Authenticated: Welcome back, {data['name']}!")
                launch_mock_dashboard("Librarian Dashboard Operational")
            else:
                error_detail = response.json().get("detail", "Authentication rejected.")
                show_error_toast(f"Access Denied: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            show_error_toast("Engine Offline: Ensure your Uvicorn FastAPI server is active on port 8000.")

    def trigger_student_otp_request(e):
        if not student_id.value.strip():
            show_error_toast("Please provide your Roll Number or Phone code first.")
            return
        
        payload = {"identifier": student_id.value.strip()}
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/student/request-otp", json=payload)
            
            if response.status_code == 200:
                show_success_toast("📡 OTP generated! Check your Uvicorn backend terminal logs for the code.")
                
                student_id.disabled = True 
                student_otp.visible = True  
                action_button.content = "Confirm Secure Entry"
                action_button.on_click = trigger_student_otp_verification
                page.update()
            else:
                error_detail = response.json().get("detail", "Student record missing.")
                show_error_toast(f"Verification Error: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            show_error_toast("Engine Offline: Ensure your Uvicorn FastAPI server is active on port 8000.")

    def trigger_student_otp_verification(e):
        payload = {
            "identifier": student_id.value.strip(),
            "otp_code": student_otp.value.strip()
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/student/verify-otp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                page.session.store.set("token", data["access_token"])
                page.session.store.set("role", data["role"])
                page.session.store.set("name", data["name"])
                
                show_success_toast("Access Token Verified successfully via stateless JWT.")
                launch_mock_dashboard("Student Portal Operational")
            else:
                error_detail = response.json().get("detail", "Invalid token.")
                show_error_toast(f"Rejected: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            show_error_toast("Engine Offline: Ensure your Uvicorn FastAPI server is active on port 8000.")

    # --- APP NOTIFICATION SHELLS ---
    def show_error_toast(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg, color=ft.Colors.WHITE), bgcolor=ft.Colors.RED_ACCENT_700)
        page.snack_bar.open = True
        page.update()
        
    def show_success_toast(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg, color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_ACCENT_700)
        page.snack_bar.open = True
        page.update()

    def launch_mock_dashboard(title_text):
        user_role = page.session.store.get("role")
        user_name = page.session.store.get("name")
        
        page.controls.clear()
        
        # --- PATH A: LIBRARIAN ADMINISTRATIVE DESKTOP PANEL ---
        if user_role == "librarian":
            page.window_width = 1200
            page.window_height = 800
            
            sidebar = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=ft.Colors.WHITE, size=24),
                        ft.Text("LMS Controller", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Text(f"Active: {user_name}", color=ft.Colors.DEEP_PURPLE_200, size=12),
                    ft.Divider(color=ft.Colors.DEEP_PURPLE_700),
                    ft.Button(content="Inventory Stock", icon=ft.Icons.MENU_BOOK, color=ft.Colors.WHITE, bgcolor=ft.Colors.TRANSPARENT),
                    ft.Button(content="Issue Engine", icon=ft.Icons.OUTPUT, color=ft.Colors.WHITE, bgcolor=ft.Colors.TRANSPARENT),
                    ft.Button(content="Active Loans", icon=ft.Icons.ASSIGNMENT, color=ft.Colors.WHITE, bgcolor=ft.Colors.TRANSPARENT),
                    ft.Divider(color=ft.Colors.DEEP_PURPLE_700),
                    # ✅ FIXED: Changed page.window_close() to modern page.window.close() API
                    ft.Button(content="Exit Safely", icon=ft.Icons.LOGOUT, color=ft.Colors.RED_200, bgcolor=ft.Colors.TRANSPARENT, on_click=lambda e: page.window.close())
                ], spacing=15),
                width=240,
                bgcolor=ft.Colors.DEEP_PURPLE_900,
                padding=20,
                border_radius=ft.BorderRadius.only(top_left=16, bottom_left=16)
            )
            
            workspace_deck = ft.Container(
                expand=True,
                padding=30,
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.BorderRadius.only(top_right=16, bottom_right=16),
                content=ft.Column([
                    ft.Text("Library Control Center", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage inventory allocations and check real-time transaction tracking analytics.", color=ft.Colors.GREY_600),
                    ft.Container(height=20),
                    
                    ft.DataTable(
                        border=ft.Border.all(width=1, color=ft.Colors.GREY_200),
                        border_radius=8,
                        heading_row_color=ft.Colors.BLUE_GREY_50,
                        columns=[
                            ft.DataColumn(ft.Text("Book Title")),
                            ft.DataColumn(ft.Text("Author")),
                            ft.DataColumn(ft.Text("ISBN ID")),
                            ft.DataColumn(ft.Text("Availability Status")),
                        ],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Core Python Systemics")),
                                ft.DataCell(ft.Text("Dr. K. Vathiyar")),
                                ft.DataCell(ft.Text("10024")),
                                ft.DataCell(ft.Text("In Stock", color=ft.Colors.GREEN_700))
                            ]),
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Asynchronous API Mastery")),
                                ft.DataCell(ft.Text("Architect Arivazhagan")),
                                ft.DataCell(ft.Text("55462")),
                                ft.DataCell(ft.Text("Issued Out", color=ft.Colors.RED_700))
                            ])
                        ]
                    )
                ], expand=True)
            )
            
            page.add(
                ft.Container(
                    content=ft.Row([sidebar, workspace_deck], spacing=0, expand=True),
                    expand=True,
                    border_radius=16,
                    shadow=ft.BoxShadow(blur_radius=20, color="#1B000000")
                )
            )

        # --- PATH B: STUDENT PORTABLE SMARTPHONE ENVIRONMENT ---
        else:
            page.window_width = 400
            page.window_height = 700
            
            page.add(
                ft.SafeArea(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Text("Namaskar,", size=14, color=ft.Colors.GREY_600),
                                    ft.Text(user_name, size=20, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=36, color=ft.Colors.DEEP_PURPLE)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=15,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=12
                        ),
                        ft.Container(height=10),
                        
                        ft.TextField(hint_text="Search available library records...", prefix_icon=ft.Icons.SEARCH, border_radius=10, bgcolor=ft.Colors.WHITE),
                        ft.Container(height=10),
                        
                        ft.Card(
                            color=ft.Colors.WHITE,
                            content=ft.Container(
                                padding=15,
                                content=ft.Column([
                                    ft.Text("Your Active Checked-Out Items", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Divider(),
                                    ft.Row([
                                        ft.Icon(ft.Icons.BOOK, color=ft.Colors.DEEP_PURPLE_400, size=20),
                                        ft.Column([
                                            ft.Text("Asynchronous API Mastery", weight=ft.FontWeight.W_500),
                                            ft.Text("Return Due: 15 Days | No Penalties", color=ft.Colors.GREEN_700, size=12)
                                        ])
                                    ])
                                ])
                            )
                        ),
                        ft.Container(expand=True),
                        # ✅ FIXED: Changed page.window_close() to modern page.window.close() API
                        ft.Button(content="Log Out Safely from Account", icon=ft.Icons.POWER_SETTINGS_NEW, on_click=lambda e: page.window.close(), bgcolor=ft.Colors.RED_50, color=ft.Colors.RED_700, width=360)
                    ], spacing=10),
                    expand=True
                )
            )
            
        page.update()

    # --- UI CONTAINERS ---
    role_selector = ft.SegmentedButton(
        selected=["student"], 
        on_change=switch_tab,
        show_selected_icon=False,
        allow_multiple_selection=False,
        segments=[
            ft.Segment(value="student", label=ft.Text("Student Portal", weight=ft.FontWeight.W_500), icon=ft.Icon(ft.Icons.PHONELINK_SETUP)),
            ft.Segment(value="librarian", label=ft.Text("Staff Login", weight=ft.FontWeight.W_500), icon=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS))
        ]
    )

    student_form = ft.Column([
        ft.Text("Access with Roll Number or Mobile No", size=13, color=ft.Colors.GREY_600),
        student_id,
        student_otp
    ], spacing=10)

    librarian_form = ft.Column([
        ft.Text("Requires administrative secure credentials", size=13, color=ft.Colors.GREY_600),
        lib_email,
        lib_pass
    ], spacing=10, visible=False)

    login_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LOCAL_LIBRARY, color=ft.Colors.DEEP_PURPLE, size=32),
                ft.Text("Vathiyar LMS", size=24, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5),
            role_selector, 
            ft.Container(height=10),
            student_form,
            librarian_form,
            ft.Container(height=15),
            action_button
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        width=360,
        bgcolor=ft.Colors.WHITE,
        padding=25,
        border_radius=16,
        shadow=ft.BoxShadow(blur_radius=15, color="#1A000000")
    )

    page.add(login_card)
    action_button.on_click = trigger_student_otp_request 

if __name__ == "__main__":
    ft.run(main)