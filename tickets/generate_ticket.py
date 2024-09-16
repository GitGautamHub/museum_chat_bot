from fpdf import FPDF
from barcode import Code128
from barcode.writer import ImageWriter
import os

class PDF(FPDF):
    def __init__(self, museum_name):
        super().__init__()
        self.museum_name = museum_name

    def header(self):
        # Draw a solid color rectangle at the top for the header
        self.set_fill_color(34, 49, 63)  # Dark blue color for the header
        self.rect(10, 10, 190, 25, 'F')  # Positioned at (10,10), width 190, height 25
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)  # White text color
        self.cell(0, 10, f'{self.museum_name} Ticket', ln=True, align='C')  # Centered museum name

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
    try:
        barcode_dir = os.path.join(os.path.dirname(__file__), 'barcodes')
        os.makedirs(barcode_dir, exist_ok=True)
        barcode = Code128(ticket_number, writer=ImageWriter())
        barcode_file = os.path.join(barcode_dir, f'barcode_{ticket_number}.png')
        barcode.save(barcode_file.replace('.png', ''))  # Saving as PNG
        return barcode_file
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def generate_ticket(booking_details):
    pdf = PDF(museum_name=booking_details["museum"])  # Pass the museum name dynamically
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Path to the background image (use 'museum.png')
    image_path = os.path.join(os.path.dirname(__file__), 'museum.png')

    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    # Add Museum Image below the header
    pdf.image(image_path, x=160, y=15, w=40, h=40)  # Positioned to the right for a balanced layout

    # Draw a box for ticket details
    pdf.set_fill_color(245, 245, 245)  # Very light gray background for the ticket details
    pdf.rect(10, 50, 120, 75, 'F')  # Rectangle for the ticket details box, narrower to fit attract image

    # Add the attraction image on the right side within the ticket box
    attract_image_path = os.path.join(os.path.dirname(__file__), 'attract.png')
    if os.path.exists(attract_image_path):
        pdf.image(attract_image_path, x=130, y=50, w=60, h=75)  # Positioned next to ticket details box

    # Booking and Ticket Details inside the box
    pdf.set_xy(15, 55)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)  # Black text for ticket details
    pdf.cell(0, 10, f'Booking Reference: {booking_details["booking_ref"]}', ln=True)
    pdf.set_xy(15, 65)
    pdf.cell(0, 10, f'Visit Date: {booking_details["visit_date"]}', ln=True)
    pdf.line(15, 75, 120, 75)  # A line to separate the header from visitor details

    # Display visitor categories neatly including Foreigners
    categories = booking_details['visitors'][0]['category']
    categories_text = f"Adults: {categories['Adults']}, Children: {categories['Children']}, Seniors: {categories['Seniors']}, Foreigners: {categories['Foreigners']}"
    pdf.set_xy(15, 80)
    pdf.cell(0, 10, categories_text, ln=True)

    y_position = 90
    for index, user in enumerate(booking_details['visitors']):
        pdf.set_xy(15, y_position)
        pdf.cell(0, 10, f'Visitor {index + 1}: {user["name"]}', ln=True)
        y_position += 10
        pdf.set_xy(15, y_position)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Ticket No: {user["ticket_number"]} | Price: Rs {user["ticket_price"]:.2f}', ln=True)
        y_position += 15  # Add some extra space for neatness

    # Generate barcode and add it below the ticket details box
    barcode_file = generate_barcode(booking_details["booking_ref"])
    if barcode_file and os.path.exists(barcode_file):
        pdf.image(barcode_file, x=15, y=y_position, w=50)  # Positioned below ticket info
    else:
        print("Failed to generate barcode, skipping barcode image.")

    # Add a thank you note or branding
    pdf.set_xy(15, y_position + 50)
    pdf.set_font('Arial', 'B', 10)  # Made bold for better visibility
    pdf.set_text_color(34, 49, 63)  # Matching dark blue
    pdf.cell(0, 10, f'Thank you for visiting {booking_details["museum"]}! Enjoy your tour.', ln=True, align='C')

    # Save the PDF to a file
    file_name = f'ticket_{booking_details["booking_ref"]}.pdf'
    pdf.output(file_name)

    # Clean up the barcode image file
    if barcode_file and os.path.exists(barcode_file):
        os.remove(barcode_file)

    print(f"Ticket saved as {file_name}")
    return file_name

# Example booking details including Foreigners
booking_details = {
    "booking_ref": "347652199854",
    "visit_date": "2024-09-03",
    "museum": "Victoria Memorial",  # Example museum name
    "visitors": [
        {
            "name": "Gautam Kumar",
            "ticket_number": "123456",
            "ticket_price": 47.00,
            "category": {"Adults": 1, "Children": 2, "Seniors": 1, "Foreigners": 1}
        }
    ]
}

# Generate the ticket
generate_ticket(booking_details)
