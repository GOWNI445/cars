from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Car
from .forms import CarForm

@login_required
def my_cars(request):
    # Only show user's own cars
    if request.user.role == 'admin':
        messages.warning(request, "Admins view all cars from the Admin Dashboard.")
        return redirect('admin_cars')
        
    cars = Car.objects.filter(user=request.user)
    return render(request, 'my_cars.html', {'cars': cars})

@login_required
def add_car(request):
    if request.user.role == 'admin':
        messages.error(request, "Admins cannot add cars.")
        return redirect('admin_service_requests')

    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            messages.success(request, f"Car {car.car_brand} {car.car_model} ({car.car_number}) added successfully!")
            return redirect('my_cars')
        else:
            messages.error(request, "Failed to add car. Please correct the errors.")
    else:
        form = CarForm()
    return render(request, 'add_car.html', {'form': form})

@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Allow owner OR admin
    if car.user != request.user and request.user.role != 'admin':
        messages.error(request, "You do not have permission to edit this car.")
        return redirect('my_cars')

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f"Car {car.car_brand} {car.car_model} updated successfully!")
            if request.user.role == 'admin':
                return redirect('admin_cars')
            return redirect('my_cars')
        else:
            messages.error(request, "Failed to update car. Please correct the errors.")
    else:
        form = CarForm(instance=car)
    return render(request, 'edit_car.html', {'form': form, 'car': car})

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Allow owner OR admin
    if car.user != request.user and request.user.role != 'admin':
        messages.error(request, "You do not have permission to delete this car.")
        return redirect('my_cars')

    if request.method == 'POST':
        car_name = f"{car.car_brand} {car.car_model}"
        car.delete()
        messages.success(request, f"Car {car_name} deleted successfully.")
        if request.user.role == 'admin':
            return redirect('admin_cars')
        return redirect('my_cars')
        
    return render(request, 'delete_car_confirm.html', {'car': car})
