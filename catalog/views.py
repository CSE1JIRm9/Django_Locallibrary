from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Language, Genre
from django.views.generic import ListView
from django.core.paginator import Paginator
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.views import generic

import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # POST 요청이면 폼 데이터를 처리한다
    if request.method == 'POST':

        # 폼 인스턴스를 생성하고 요청에 의한 데이타로 채운다 (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # 폼이 유효한지 체크한다:
        if book_renewal_form.is_valid():
            # form.cleaned_data 데이타를 요청받은대로 처리한다(여기선 그냥 모델 due_back 필드에 써넣는다)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()

            # 새로운 URL로 보낸다:
            return HttpResponseRedirect(reverse('borrowed') )

    # GET 요청 (혹은 다른 메소드)이면 기본 폼을 생성한다.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/bookinstance_all_borrowed_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

def index(request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_search = Book.objects.filter(title__icontains='니').count()
    genre_search = Genre.objects.filter(name__icontains="R").count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_authors': num_authors,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_search' : num_search,
        'genre_search' : genre_search,
        'num_visits': num_visits,
    }

    return render(request, 'index.html',context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    model = Book
    paginate_by = 2
    context_object_name = 'book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='니')[:3] # Get 5 books containing the title war
    #template_name = 'books/book_list.html'  # Specify your own template name/location

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

# 걍 질문해 개색기야
class AuthorDetailView(generic.DetailView):
    model = Author

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
