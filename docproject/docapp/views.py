# Developer name: Phala Mathobela(phalamat676@gmail.com)
# The application allows the user to upload a financial pdf document, and then it gets converted into excel format.
# The user can then donwload the excel format 
from django.shortcuts import render, redirect
from . forms import CreateUserForm, LoginForm
from django.contrib.auth.decorators import login_required
#doc start
import os
from django.http import HttpResponse
from .forms import UploadFileForm
import pdfplumber
import pandas as pd
from django.conf import settings
#doc end

# feedback
from .forms import FeedbackForm
from .models import Feedback
from django.core.mail import send_mail
from django.contrib import messages
#

#Authetication models and forms
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

# Create views here.
def homepage(request):
    
    return render(request,'docapp/index.html')

# Document upload code starts here
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            if uploaded_file.content_type != 'application/pdf':
                return render(request, 'docapp/upload_failed.html', {
                    'error': 'Only PDF files are allowed.'
                })

            file_path = handle_uploaded_file(uploaded_file)
            df = extract_table_from_pdf(file_path)  # Call the function to extract the data from the PDF file.

            if df is None:
                return render(request, 'docapp/upload_failed.html', {
                    'error': 'No tables found in the uploaded PDF'
                })

            # Save to Excel
            excel_path = file_path.replace('.pdf', '.xlsx')
            df.to_excel(excel_path, index=False)
            print(f"Excel saved at: {excel_path}")

            # Auto-delete the uploaded file after conversion
            os.remove(file_path)

            return render(request, 'docapp/upload_success.html', {
                'excel_path': excel_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL),
            })
    else:
        form = UploadFileForm()
    return render(request, 'docapp/upload_file.html', {'form': form})

# Extracting information from the uploaded file
def extract_table_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                tables.extend(table)

    # Check if tables were extracted
    if not tables:
        print("No tables found in PDF")
        return None

    max_columns = max(len(row) for row in tables)
    padded_tables = [row + [None] * (max_columns - len(row)) for row in tables]
    df = pd.DataFrame(padded_tables[1:], columns=padded_tables[0])
    return df

def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print(f"File saved to {file_path}")
    return file_path
         
#--Document upload and conversion code ends here

# Feedback form on the upload_file landing page
def feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        comments = request.POST.get('comments')

        # Send an email to the feedback@makeitxl.com
        subject = f'Feedback from {name}'
        message = f'Name: {name}\nEmail: {email}\n\nComments:\n{comments}'
        recipient_list = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, email, recipient_list)

        # success message
        messages.success(request, 'Thank you for your feedback!')

        return redirect('upload_file')  # Redirect to a page after submission
    else:
        return redirect('upload_file')  # Redirect to a page if not a POST request