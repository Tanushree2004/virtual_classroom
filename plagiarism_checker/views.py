from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import PlagiarismCheckForm
from .utils import compare_texts, extract_text_from_pdf, extract_text_from_docx
from django.contrib.auth.decorators import login_required

ALLOWED_EXTENSIONS = ['.txt', '.csv', '.md', '.pdf', '.docx']  # Added .docx support

def is_valid_file(file):
    """Checks if the uploaded file is a valid text, CSV, Markdown, PDF, or DOCX file."""
    return any(file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def read_file_content(file):
    """Reads content from text, CSV, Markdown, PDF, or DOCX files."""
    try:
        if file.name.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            return extract_text_from_docx(file)
        return file.read().decode('utf-8', errors='replace')
    except UnicodeDecodeError:
        return None
@login_required
def plagiarism_checker_view(request):
    similarity_score = None
    highlighted_text1 = None
    highlighted_text2 = None

    if request.method == 'POST':
        form = PlagiarismCheckForm(request.POST, request.FILES)
        
        if form.is_valid():
            file1 = request.FILES.get('file1')
            file2 = request.FILES.get('file2')

            if not file1 or not file2:
                return JsonResponse({'error': 'Both files are required.'}, status=400)

            if not (is_valid_file(file1) and is_valid_file(file2)):
                return JsonResponse({'error': 'Only .txt, .csv, .md, .pdf, or .docx files are allowed.'}, status=400)

            text1 = read_file_content(file1)
            text2 = read_file_content(file2)

            if text1 is None or text2 is None:
                return JsonResponse({'error': 'Unable to read one or both files. Ensure they are text-based or PDF/DOCX files.'}, status=400)

            if not text1.strip() or not text2.strip():
                return JsonResponse({'error': 'Files must not be empty.'}, status=400)

            # Compute similarity and matching highlights
            similarity_score, highlighted_text1, highlighted_text2 = compare_texts(text1, text2)

    else:
        form = PlagiarismCheckForm()

    return render(
        request,
        "plagiarism_checker/check.html",
        {
            "form": form,
            "similarity": similarity_score,
            "highlighted_text1": highlighted_text1,
            "highlighted_text2": highlighted_text2,
        },
    )
