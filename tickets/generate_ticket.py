from fpdf import FPDF
from barcode import Code128
from barcode.writer import ImageWriter
import os

class PDF(FPDF):
    def header(self):
        # Draw a solid color rectangle at the top for the header
        self.set_fill_color(34, 49, 63)  # Dark blue color for the header
        self.rect(10, 10, 190, 25, 'F')  # Positioned at (10,10), width 190, height 25
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)  # White text color
        self.cell(0, 10, 'National Museum of Delhi Ticket', ln=True, align='C')

    def footer(self):
        # Position for the rules at the bottom
        self.set_y(-60)
        self.set_font('Arial', 'B', 8)  # Made bold for better visibility
        self.set_text_color(50, 50, 50)  # Dark gray text color
        self.multi_cell(0, 10, 'Rules & Regulations:\n'
                               '1. Please carry a valid ID proof.\n'
                               '2. No food or drinks allowed inside the museum premises.\n'
                               '3. Maintain silence inside exhibition halls.\n'
                               '4. Follow the guide and keep to the designated pathways.\n'
                               '5. Tickets are non-refundable and non-transferable.', align='L')

def generate_barcode(ticket_number):
    barcode_dir = os.path.join(os.path.dirname(__file__), 'barcodes')
    os.makedirs(barcode_dir, exist_ok=True)

    barcode = Code128(ticket_number, writer=ImageWriter())
    barcode_file = os.path.join(barcode_dir, f'barcode_{ticket_number}.png')
    barcode.save(barcode_file.replace('.png', ''))
    return barcode_file

def generate_ticket(booking_details):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Path to the background image (if needed)
    image_path = os.path.join(os.path.dirname(__file__), 'ticket_img.jpeg')
    
    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    # Add Museum Image below the header
    pdf.image(image_path, x=160, y=15, w=40, h=40)  # Positioned to the right for a balanced layout

    # Draw a box for ticket details
    pdf.set_fill_color(245, 245, 245)  # Very light gray background for the ticket details
    pdf.rect(10, 45, 190, 75, 'F')  # Rectangle for the ticket details box

    # Booking and Ticket Details inside the box
    pdf.set_xy(15, 50)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)  # Black text for ticket details
    pdf.cell(0, 10, f'Booking Reference: {booking_details["booking_ref"]}', ln=True)
    pdf.set_xy(15, 60)
    pdf.cell(0, 10, f'Visit Date: {booking_details["visit_date"]}', ln=True)
    pdf.line(15, 70, 195, 70)  # A line to separate the header from visitor details

    y_position = 75
    for index, user in enumerate(booking_details['visitors']):
        pdf.set_xy(15, y_position)
        pdf.cell(0, 10, f'{user["category"]} {index + 1}: {user["name"]}', ln=True)
        y_position += 10
        pdf.set_xy(15, y_position)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Ticket No: {user["ticket_number"]} | Price: Rs {user["ticket_price"]:.2f}', ln=True)
        y_position += 15  # Add some extra space for neatness

    # Add barcode below the ticket details box
    barcode_file = generate_barcode(booking_details["booking_ref"])
    pdf.image(barcode_file, x=15, y=y_position, w=50)  # Positioned below ticket info

    # Add a thank you note or branding
    pdf.set_xy(15, y_position + 50)
    pdf.set_font('Arial', 'B', 10)  # Made bold for better visibility
    pdf.set_text_color(34, 49, 63)  # Matching dark blue
    pdf.cell(0, 10, 'Thank you for visiting the National Museum of Delhi! Enjoy your tour.', ln=True, align='C')

    # Save the PDF to a file
    file_name = f'ticket_{booking_details["booking_ref"]}.pdf'
    pdf.output(file_name)

    # Clean up the barcode image file
    os.remove(barcode_file)

    print(f"Ticket saved as {file_name}")
    return file_name

# Example booking details
booking_details = {
    "booking_ref": "347652199854",
    "visit_date": "2024-09-03",
    "visitors": [
        {"name": "John Doe", "ticket_number": "123456", "ticket_price": 20, "category": "Adult"}
    ]
}

# Generate the ticket
generate_ticket(booking_details)
