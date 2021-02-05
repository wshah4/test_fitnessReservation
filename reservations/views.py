from datetime import date, time
from django.utils import timezone
from django.shortcuts import render, redirect
from datetime import datetime, date
from . models import Reservation, WaitList
from fitnessClass.models import FitnessClass
from accounts.models import Customer
from accounts.forms import staffCustomerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



# Create your views here.
@login_required(login_url="accounts:login")
def reserve_view(request):
    customerForm = None
    firstName = None
    lastName = None
    phoneNumber = None
    duplicate = False
    duplicateMessage = ''
    currentUser = request.user
    if request.method == 'POST':
        if currentUser.is_staff:
            customerForm = staffCustomerForm()
            if customerForm.is_valid():
                firstName = customerForm.cleaned_data.get('firstName')
                lastName = customerForm.cleaned_data.get('lastName')
                phoneNumber = customerForm.cleaned_data.get('phoneNumber')
        statement = ''
        className = request.POST.get('className')
        instructorName = request.POST.get('instructorName')
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        classDate = request.POST.get('date')
        classId = request.POST.get('classId')
        today = (date.today().strftime('%m-%d-%Y'))
        dateFormated = formatDate(classDate)        
        (available, max) = availability(classId, dateFormated)
        if available < 1:
            temp_available = f'{-(available)}'
            available = temp_available
            availabilityTitle = 'Position on WaitList'
            available = (int(available) + 1)
        elif available >= 10:
            availabilityTitle = 'OverDraft Room Availability'
        else:
            availabilityTitle = 'Availability'
        if currentUser.is_staff == False:
            (duplicate, duplicateMessage) = checkDuplicateReservation(getCustomer(request), dateFormated, getFitnessClass(classId))
        (classPassedFlag, classPassedMessage) = checkClassPassed(getFitnessClass(classId), dateFormated)
        rv = {
            'statement': statement,
            'className':className,
            'instructorName':instructorName,
            'startTime':startTime,
            'endTime':endTime,
            'classDate':classDate ,
            'today': today,
            'availabilityTitle': availabilityTitle,
            'available':available,
            'classId':classId,
            'duplicate':duplicate,
            'duplicateMessage':duplicateMessage,
            'classPassedFlag': classPassedFlag,
            'classPassedMessage': classPassedMessage,
            'customerForm': customerForm,
            'currentUser': currentUser
        }
        return render(request, 'reservations/reserve.html', rv)
    else:
        return redirect('fitnessClass:schedule')

@login_required(login_url="accounts:login")
def submission_view(request):
    submitted = request.POST.get('submitted')
    currentUser = request.user
    classId = request.POST.get('classId')
    classDate = request.POST.get('classDate')
    dateFormated = formatDate(classDate)
    (available, max) = availability(classId, dateFormated)
    statement = {}
    statement['currentUser'] = currentUser
    list = FitnessClass.objects.all().filter(id = classId)

    fitnessClass = ''
    for i in list:
        fitnessClass = i
   
    reservationInstance = Reservation()
    reservationInstance.classReserved = fitnessClass
    duplicateFlag = False
    statement['duplicateFlag'] = duplicateFlag
    if currentUser.is_staff:
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        phoneNumber = request.POST.get('phoneNumber')
        customerList = Customer.objects.values_list('id', flat=True).filter(firstName = firstName, lastName = lastName, phoneNumber = phoneNumber)
        (flag, value) = checkDuplicateReservationStaff(firstName, lastName, phoneNumber, classId, dateFormated)
        if flag == True:
            statement['duplicateReservationMessage']= (f'{value}')
            duplicateFlag = True
        else:
            if len(customerList) <= 0:
                # create a new customer and assign all values, including adding a user account
                customer = Customer()
                customer.email = 'temporaryEmail@email.com'
                customer.firstName = firstName
                customer.lastName = lastName
                customer.phoneNumber = phoneNumber
                if submitted == 'True':
                    customer.save()
                reservationInstance.customerReserving = customer
            else:
                list = Customer.objects.all().filter(firstName = firstName, lastName = lastName, phoneNumber = phoneNumber)
                for i in list:
                    reservationInstance.customerReserving = i
    else:
        reservationInstance.customerReserving = getCustomer(request)

    if duplicateFlag == False:
        reservationInstance.classDate = dateFormated
        reservationInstance.reservationDate = date.today()
        reservationInstance.reservationTime = datetime.now().time()

        statement['classDate'] = classDate
        statement['classReserved'] = reservationInstance.classReserved
        statement['customerReserving'] =  reservationInstance.customerReserving
        
        temp_waitList = WaitList()
        temp_waitList.save()
        nId = temp_waitList.id
        
        if int(max) > 9:
            if int(available) > 10:
                reservationInstance.reservationStatus = 'Reserved'
            elif int(available) <= 10 and int(available) > 0:
                reservationInstance.reservationStatus = 'OverDraft'
            else:
                reservationInstance.reservationStatus = 'WaitList'
                reservationInstance.waitNumber = nId
        else:
            if int(available) > 0:
                reservationInstance.reservationStatus = 'Reserved'
            else:
                reservationInstance.reservationStatus = 'WaitList'
                reservationInstance.waitNumber = nId
        
        if submitted == 'True':
            reservationInstance.save()
            
        statement['reservationStatus'] = reservationInstance.reservationStatus
        waitList = getWaitListPosition(dateFormated, reservationInstance)
        statement['waitListPosition'] = 0
        if waitList > 0:
            statement['waitListPosition'] = waitList + 1
        statement['currentUser'] = currentUser
        return render(request, 'reservations/submission.html', statement)
    else:
        return render(request, 'reservations/submission.html', statement)

@login_required(login_url="accounts:login")
def myReservations_view(request):
    returnValue = []  
    if request.method == 'POST':
        reservationId = request.POST.get('reservationId')
        intId = Reservation.objects.values_list('id', flat=True).filter(id = reservationId)
        temp_id = intId[0]
        Reservation.objects.filter(id = temp_id).delete()
    currentUser = request.user
    customer = Customer.objects.all().filter(user = currentUser)
    customerId = ''
    for i in customer:
        customerId = i
    todaysDate = date.today()
    select = Reservation.objects.all().filter(customerReserving = customerId).order_by('-classDate')
    for i in select:
        if i.reservationDate >= todaysDate:
            returnValue.append(i) 
    return render(request, 'reservations/myReservations.html', {'reservations':returnValue})

def staffReservations_view(request):
    rv = {}
    if request.method == 'GET':
        rv['flag'] = True
        select = FitnessClass.objects.all().order_by("-dayOfWeek")
        classList = {}
        counter = 0
        for i in select:
            counter = i.id            
            classList[counter] = i
        rv['classList'] = classList
        return render(request, 'reservations/staffReservations.html', rv)
    else:
        action = request.POST.get('action')
        if action == 'cancel':
            temp_id = request.POST.get('reservationId')
            Reservation.objects.filter(id = temp_id).delete()
        elif action == 'overDraftToReserved':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'Reserved'
            r.save()
        elif action == 'waitListToOverDraft':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'OverDraft'
            r.save()
        elif action == 'waitListToReserved':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'Reserved'
            r.save()
        else:
            ''

        classId = request.POST.get('classId')
        select = Reservation.objects.all().filter(classReserved = getFitnessClass(classId)).order_by('reservationTime')
        reservedList = {}
        waitList = {}
        overDraftList = {}
        #enter code to send back the classes ID and present the staff memebers with the table 
        counter = 0
        reservedCounter = 0
        overDraftCounter = 0
        waitListCounter = 0
        className = ''
        classMaximum = 0
        for i in select:
            className = i.classReserved.className
            classMaximum = i.classReserved.maximumCapacity
            (flag, value) = checkDate(i.classDate)
            if flag == True:
                counter = i.id
                if i.reservationStatus == "Reserved":
                    reservedList[counter] = i
                    rv['reservedList'] = reservedList
                    reservedCounter += 1
                elif i.reservationStatus == "WaitList":
                    waitList[counter] = i
                    rv['waitList'] = waitList
                    waitListCounter += 1
                else:
                    overDraftList[counter] = i
                    rv['overDraftList'] = overDraftList
                    overDraftCounter += 1
            else:
                rv['statement'] = value
                rv['flag'] = False
                return render(request, 'reservations/staffReservations.html', rv)
        reservedAndOverDraftTotal = reservedCounter + overDraftCounter
        rv['reservedCounter'] = reservedCounter
        rv['waitListCounter'] = waitListCounter
        rv['overDraftCounter'] = overDraftCounter
        rv['flag'] = False
        rv['className'] = className
        rv['classMaximum'] = int(classMaximum)
        rv['overDraftMaximum'] = 10
        rv['reservedAndOverDraftTotal'] = reservedAndOverDraftTotal
        return render(request, 'reservations/staffReservations.html', rv)

def availability(classId, date):
    count = Reservation.objects.filter(classDate = date, classReserved = classId).count()
    max = FitnessClass.objects.values_list('maximumCapacity', flat=True).get(id=classId)
    available = int(max) - count
    return (available, max)

# '01-01-2021' --> 2021-01-01
def formatDate(date):
    dateStr = date[6:] + '-' + date[0:2] + '-' + date[3:5]
    return (dateStr)

def checkDate(dateOfClass):
    temp_classDate = str(dateOfClass)
    classDate = temp_classDate[0:10]
    todayDate = date.today().strftime('%Y-%m-%d')
    if classDate < todayDate:
        return (False, 'The class date is in past')
    else:
        return (True, 'Today greater than today date')

def getCustomer(request):
    customerId = request.user.id
    list = Customer.objects.all().filter(user = customerId)
    customer = ''
    for i in list:
        customer = i
    return customer

def getFitnessClass(classId):
    list = FitnessClass.objects.all().filter(id = classId)
    fitnessClass = ''
    for i in list:
        fitnessClass = i
    return fitnessClass

def getWaitListPosition(dateOfClass, currentReservation):
    list = Reservation.objects.filter(classReserved = currentReservation.classReserved, classDate = dateOfClass, reservationStatus = "WaitList")
    count = 0
    for line in list:
        waitNumber = line.waitNumber
        if waitNumber > 0 and waitNumber < currentReservation.waitNumber:
            count += 1
    return count

def cancelFunction(dateOfClass, currentWaitNumber):
    list = Reservation.objects.filter(classDate = dateOfClass)
    waitList = []
    id = ''
    for line in list:
        waitNumber = line.waitNumber
        if waitNumber > 0 and waitNumber < currentWaitNumber:
            tempWait = min(waitList)
            if waitNumber < tempWait:
                id = line.id
    return id

#checks for duplicate reservations when a customer is reserving
def checkDuplicateReservation(customer, dateOfClass, classId):
    count = Reservation.objects.filter(customerReserving = customer, classReserved = classId, classDate = dateOfClass).count()
    if count > 0 :
        return (True, f'* You have already reserved for this class')
    else:
        return (False, '')

def checkDuplicateReservationStaff(firstName, lastName, phoneNumber, classId, dateOfClass):
    reservations = Reservation.objects.filter(classReserved = classId, classDate = dateOfClass)
    count = 0
    for r in reservations:
        if r.customerReserving.firstName.lower() == firstName.lower() and r.customerReserving.lastName.lower() == lastName.lower() and r.customerReserving.phoneNumber.lower() == phoneNumber.lower():
            count += 1
    if count > 0 :
        return (True, f'* You have already reserved for this class')
    else:
        return (False, '')

def checkClassPassed(fitnessClass, classDate):
    returnedStartTime = FitnessClass.objects.values_list('startTime', flat=True).filter(id = fitnessClass.id)
    given_time = returnedStartTime[0] #fitness class start time
    now = datetime.now()
    current_time = now.strftime('%I:%M %p')
    t = ''
    
    temp_classDate = str(classDate)
    classDate = temp_classDate[0:10]
    todayDate = date.today().strftime('%Y-%m-%d')
    flag = True
    if classDate < todayDate:
        flag = False
        t =  'The class date is in past'
    elif todayDate == classDate:
        if given_time[6:8] == 'AM' and current_time[6:8] == 'PM':
            t = '* Reservation for past class cannot be made.'
            flag = False
        else: # same part of day
            if int(given_time[0:2]) > int(current_time[0:2]): # compare Hour
                t = '1 * Can Reserve'
            elif int(given_time[0:2]) < int(current_time[0:2]):
                t = 'Unable to reserve for classes in the past'
                flag = False
            else:
                if int(given_time[3:5]) > int(current_time[3:5]): # compare Minute
                    t = ''
                elif int(given_time[3:5]) < int(current_time[3:5]):
                    flag = False
                    t = 'Unable to reserve, this class has already started'
                else:
                    flag = False
    else:
        t=''
        flag = True

    return(flag, t)