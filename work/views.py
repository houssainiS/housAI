from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from login.models import User
import openai
from django.http import JsonResponse
import environ
from django.core.exceptions import ImproperlyConfigured
import os
import re
from .models import GeneratedWebsite , Template


# Initialize environ
env = environ.Env()
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
environ.Env.read_env(env_file)

# AI API settings
try:
    openai.api_key = env('OPENAI_API_KEY')
except KeyError:
    raise ImproperlyConfigured("Set the OPENAI_API_KEY environment variable")

# DALL·E 2 image generation function
from openai import OpenAI
client = OpenAI()

def ask_dalle_2(prompt):
    """Generates an image from DALL·E 2 based on the given prompt using the new API."""
    try:
        # Make the API call to generate the image
        response = client.images.generate(
            prompt=prompt,  # Use the prompt provided
            size="256x256",  # Use supported size (256x256)
            quality="standard",  # Quality setting
            n=1,
        )
        
        # Extract the URL of the generated image
        image_url = response.data[0].url
        
        print(f"Image generated for prompt: {prompt}")
        return image_url
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def ask_openai(message):
    """Generates the HTML, CSS, and JS from OpenAI based on user input."""
    prompt = f"""Generate a high-quality, responsive website layout based on the following description: {message}.

Return only the **contents** of the following tags, and always include all three even if they're empty: `<body>`, `<style>`, and `<script>` — e.g., `<script></script>`.

Instructions:
- The `<body>` should contain clean, semantic HTML structure with well-labeled sections and use appropriate HTML5 elements (e.g., <header>, <nav>, <section>, <main>, <footer>).
- Use responsive HTML and CSS best practices (flexbox/grid layout, media queries, scalable units like %, rem, em). Prioritize mobile-first design.
- All layout styling must be included inside the `<style>` tag using **internal CSS only**. Do not use inline styles or external files.
- The `<style>` must ensure cross-device responsiveness (mobile, tablet, desktop) and use accessible contrast ratios and modern fonts.
- Any `<img>` must include a descriptive `alt` attribute.
- If there are `<img>` tags, **ensure images always fully fit inside their containers without breaking the layout** (e.g., using `object-fit: cover`, `max-width: 100%`, `height: auto`).
- The `<script>` tag must include **working internal JavaScript** (if the design includes interactivity like toggles, modals, dropdowns, etc.), otherwise leave it empty.
- If there is interactive behavior (menus, modals, toggles), ensure the JS code properly adds/removes classes, and is scoped only to the included HTML.
- Do **not** include `<html>`, `<head>`, `<title>`, or any external links like `<link>` or `<script src=...>`.
- Do not use frameworks like Bootstrap or libraries like jQuery.

Output format: strictly return the `<body>`, then `<style>`, then `<script>` tags — in that order, and nothing else.
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5000,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def extract_code_parts(ai_response, generate_images):
    """Extract only the CSS, JavaScript, and HTML body content from the AI response and generate images if needed."""
    
    print("Full AI response:")
    print(ai_response)
    print("\n" + "="*50 + "\n")  # Separator for better readability

    ai_response = re.sub(r"```(html|css|javascript)?\s*([\s\S]*?)```", r"\2", ai_response)

    body_match = re.search(r"<body[\s\S]*?</body>", ai_response, re.DOTALL | re.IGNORECASE)
    css_match = re.search(r"<style[\s\S]*?</style>", ai_response, re.DOTALL | re.IGNORECASE)
    js_match = re.search(r"<script[\s\S]*?</script>", ai_response, re.DOTALL | re.IGNORECASE)

    body_content = body_match.group(0) if body_match else "No body content found."
    css_content = css_match.group(0) if css_match else "No CSS content found."
    js_content = js_match.group(0) if js_match else "No JS content found."
    
    # Check if image generation is enabled and if there are image tags in the body content
    if generate_images:
        img_tags = re.findall(r'<img [^>]*src="([^"]+)', body_content)
        print(f"Found {len(img_tags)} image(s) in the body content.")

        # Replace image sources with generated URLs
        for img_tag in img_tags:
            generated_image_url = ask_dalle_2(img_tag)  # Generate the image based on the prompt
            if generated_image_url:
                body_content = body_content.replace(img_tag, generated_image_url)

        # Print the body content after replacements
        print("\nModified Body Content After Replacing Image URLs:")
        print(body_content)

    return {
        "body": body_content,
        "css": css_content,
        "js": js_content
    }

def get_ai_response(request, user_id):
    user_message = request.GET.get("userMessage", "")
    generate_images = request.GET.get("generateImages", "false").lower() == "true"  # Capture the image switch state
    if not user_message:
        return JsonResponse({"error": "No message provided"}, status=400)

    ai_response = ask_openai(user_message)
    extracted_code = extract_code_parts(ai_response, generate_images)  # Pass the generateImages flag

    return JsonResponse(extracted_code)


# Ensure user is authenticated before accessing views
@login_required(login_url='login')
def home(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        return redirect('home', user_id=request.user.id)
    return render(request, 'work/home.html', {'user': user})


@login_required(login_url='login')
def advanced_mode(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        return redirect('home', user_id=request.user.id)
    return render(request, 'work/advancedMode.html', {'user': user})


@login_required
def save_generated_website(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        prompt = request.POST.get('prompt')
        body = request.POST.get('body', '')  # Assuming body is passed via AJAX
        css = request.POST.get('css', '')  # Optional, if you're passing css as well
        js = request.POST.get('js', '')    # Optional, if you're passing js as well
        
        # Create a new GeneratedWebsite instance and save it
        website = GeneratedWebsite.objects.create(
            user=request.user,
            title=title,
            body=body,
            css=css,
            js=js,
            prompt=prompt,
        )

        # Return a JSON response to indicate success
        return JsonResponse({'message': 'Website saved successfully!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)



###################history page
# History page function
@login_required
def history(request, user_id):
    user = get_object_or_404(User, id=user_id)  # Get the user by ID
    saved_websites = GeneratedWebsite.objects.filter(user=user).order_by('-created_at')  # Filter by the logged-in user
    return render(request, 'work/history.html', {'saved_websites': saved_websites})


@login_required
def view_saved_website(request, user_id, website_id):
    website = get_object_or_404(GeneratedWebsite, id=website_id)
    return render(request, 'work/view_saved_website.html', {'website': website})



#see code page
def view_code(request, user_id, website_id):
    website = get_object_or_404(GeneratedWebsite, id=website_id)

    # Construct the full code including CSS, Body, and JS
    full_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{website.title}</title>
    <style>{website.css}</style>  <!-- Ensure CSS is included -->
</head>
<body>
    {website.body}
    <script>{website.js}</script>  <!-- Ensure JS is included -->
</body>
</html>"""

    # Split full code into lines for proper display
    code_lines = full_code.splitlines()

    return render(request, 'work/code.html', {
        'website': website,
        'code_lines': code_lines
    })

#demo page

def demo(request, user_id, website_id):
    website = get_object_or_404(GeneratedWebsite, id=website_id)
    return render(request, 'work/demo.html', {'website': website})

#editing page

@login_required
def edit_website(request,user_id, website_id):
    website = get_object_or_404(GeneratedWebsite, id=website_id)

    if request.method == "POST":
        new_body = request.POST.get("body", "")  # Get the updated body content
        website.body = new_body  # Update only the body
        website.save()  # Save changes

        return JsonResponse({"success": True})  # Return success response

    return render(request, "work/edit.html", {"website": website})

#delete 1 history 

@login_required
def delete_website(request, website_id):
    website = get_object_or_404(GeneratedWebsite, id=website_id, user=request.user)
    website.delete()
    return JsonResponse({"success": True})

#templates

@login_required
def templates(request, user_id):
    templates = Template.objects.all()
    return render(request, 'work/templates_page.html', {'templates': templates, 'user_id': user_id})

@login_required
def view_template(request, user_id, template_id):
    # Fetch the template based on the provided ID
    template = get_object_or_404(Template, id=template_id)
    
    # You can pass additional context like user information if needed
    return render(request, 'work/template_view.html', {'template': template, 'user_id': user_id})
@login_required
def template_demo(request, user_id, website_id):
    template = get_object_or_404(Template, id=website_id)
    return render(request, 'work/template_demo.html', {'template': template})

@login_required
def template_code(request, user_id, website_id):
    template = get_object_or_404(Template, id=website_id)
    code_lines = template.code.splitlines()
    return render(request, 'work/template_code.html', {
        'template': template,
        'code_lines': code_lines,
    })

@login_required
def save_template(request, user_id, website_id):
    # Get the template object
    template = get_object_or_404(Template, id=website_id)

    # The full template code
    template_code = template.code

    # Regular expressions to match content inside <body>, <style>, and <script> tags
    body_pattern = re.compile(r'<body.*?>(.*?)</body>', re.DOTALL)
    style_pattern = re.compile(r'<style.*?>(.*?)</style>', re.DOTALL)
    script_pattern = re.compile(r'<script.*?>(.*?)</script>', re.DOTALL)

    # Extract content for body, style, and script using regex
    body_content = re.search(body_pattern, template_code)
    style_content = re.search(style_pattern, template_code)
    script_content = re.search(script_pattern, template_code)

    # Set to empty string if not found
    body_content = body_content.group(1) if body_content else ''
    style_content = style_content.group(1) if style_content else ''
    script_content = script_content.group(1) if script_content else ''

    # Check if title is provided via AJAX
    if request.method == "POST":
        title = request.POST.get('title')  # Get title from the form

        if title:
            # Save the content in the GeneratedWebsite model
            generated_website = GeneratedWebsite.objects.create(
                user=request.user,
                title=title,
                body=body_content,
                css=style_content,
                js=script_content,
                prompt="Its a Saved Template not a generated Website"  # Save the original template code as prompt
            )

            # Redirect the user or return a response as needed
            return redirect('work:see_template', user_id=user_id, template_id=website_id)


    # If no title provided (or GET request), just redirect back
    return redirect('work:see_template', user_id=user_id, template_id=website_id)




#profile & settings 

def profile_view(request,user_id):
    return render(request, 'work/profile.html')



@login_required
def settings_view(request):
    return render(request, 'work/settings.html')


@login_required
def update_settings(request):
    if request.method == 'POST':
        new_username = request.POST['username']
        new_email = request.POST['email']

        # Check if the new username already exists
        if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            return render(request, 'work/settings.html', {'username_error': 'Username is already taken.'})

        # Check if the new email already exists
        if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
            return render(request, 'work/settings.html', {'email_error': 'Email is already in use.'})

        # Update the username and email if no duplicates
        request.user.username = new_username
        request.user.email = new_email
        request.user.save()

        success = True
        return render(request, 'work/settings.html', {'profile_updated': True, 'success': success})

    return render(request, 'work/settings.html')


@login_required
def change_password(request):
    if request.method == 'POST' and 'old_password' in request.POST:
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the old password is correct
        if not user.check_password(old_password):
            return render(request, 'work/settings.html', {'password_error': True})

        # Check if the new passwords match
        if new_password != confirm_password:
            return render(request, 'work/settings.html', {'password_mismatch': True})

        # Set the new password and save it
        user.set_password(new_password)
        user.save()

        # Update session hash after password change
        update_session_auth_hash(request, user)

        return render(request, 'work/settings.html', {'password_updated': True})

    return render(request, 'work/settings.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('login:login')  # Or homepage