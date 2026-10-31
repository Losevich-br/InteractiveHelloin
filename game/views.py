import base64
from io import BytesIO
import qrcode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Activity, Event, Participant, ScoreEntry

def home(request):
    if request.user.is_authenticated and hasattr(request.user, "participant"):
        return render(request, "game/home.html", {"participant": request.user.participant, "events": request.user.participant.events.all()})
    return render(request, "game/home.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        password = request.POST.get("password", "")
        if request.POST.get("consent") != "yes":
            messages.error(request, "Для регистрации нужно принять условия участия.")
        elif len(nickname) > 32 or not nickname or not username:
            messages.error(request, "Укажите логин и никнейм (до 32 символов).")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Этот логин уже занят.")
        else:
            candidate = User(username=username)
            try:
                validate_password(password, candidate)
            except ValidationError as error:
                messages.error(request, " ".join(error.messages))
            else:
                user = User.objects.create_user(username=username, password=password)
                Participant.objects.create(user=user, nickname=nickname)
                login(request, user)
                return redirect("home")
    return render(request, "game/register.html")

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            return redirect("host" if user.is_staff else "home")
        messages.error(request, "Неверный логин или пароль.")
    return render(request, "game/login.html")

@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
@require_POST
def join_event(request):
    code = request.POST.get("code", "").strip().upper()
    event = Event.objects.filter(join_code=code, is_active=True, is_finished=False).first()
    if not event:
        messages.error(request, "Код не найден или регистрация на событие закрыта.")
    elif not hasattr(request.user, "participant"):
        messages.error(request, "Ведущие не могут присоединяться как участники.")
    else:
        event.participants.add(request.user.participant)
        messages.success(request, f"Вы подключились к событию «{event.title}».")
    return redirect("home")

@login_required
@require_POST
def change_nickname(request):
    if not hasattr(request.user, "participant"):
        return HttpResponseForbidden()
    nickname = request.POST.get("nickname", "").strip()
    if nickname and len(nickname) <= 32:
        request.user.participant.nickname = nickname
        request.user.participant.save(update_fields=["nickname"])
        messages.success(request, "Никнейм обновлён.")
    else:
        messages.error(request, "Никнейм должен содержать от 1 до 32 символов.")
    return redirect("home")

@login_required
def participant_stats(request):
    if not hasattr(request.user, "participant"):
        return redirect("host")
    participant = request.user.participant
    summaries = []
    for event in participant.events.all():
        entries = ScoreEntry.objects.filter(activity__event=event, participant=participant)
        summaries.append({"event": event, "total": entries.aggregate(total=Sum("points"))["total"] or 0,
                          "activities": event.activities.all()})
    return render(request, "game/stats.html", {"participant": participant, "summaries": summaries})

def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff)(view))

@staff_required
def host_dashboard(request):
    return render(request, "game/host.html", {"events": Event.objects.filter(host=request.user).order_by("-created_at")})

@staff_required
@require_POST
def create_event(request):
    title = request.POST.get("title", "").strip()
    if title:
        event = Event.objects.create(title=title[:120], host=request.user)
        messages.success(request, f"Событие создано. Код: {event.join_code}")
    return redirect("host")

@staff_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, host=request.user)
    rows = []
    for participant in event.participants.order_by("nickname"):
        per_activity = {a.id: 0 for a in event.activities.all()}
        total = 0
        for score in ScoreEntry.objects.filter(activity__event=event, participant=participant):
            per_activity[score.activity_id] = per_activity.get(score.activity_id, 0) + score.points
            total += score.points
        rows.append({"participant": participant, "scores": per_activity, "total": total})
    qr = qrcode.make(request.build_absolute_uri("/register/"))
    buffer = BytesIO(); qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()
    winner = rows[0] if rows else None
    for row in rows:
        if winner is None or row["total"] > winner["total"]:
            winner = row
    return render(request, "game/event.html", {"event": event, "activities": event.activities.all(), "rows": rows, "qr_data": qr_data,
                                                  "winner": winner if event.is_finished else None, "join_url": request.build_absolute_uri("/register/")})

@staff_required
@require_POST
def create_activity(request, event_id):
    event = get_object_or_404(Event, pk=event_id, host=request.user, is_finished=False)
    title = request.POST.get("title", "").strip()
    if title:
        Activity.objects.create(event=event, title=title[:120], description=request.POST.get("description", "")[:1000])
        messages.success(request, "Интерактив добавлен.")
    return redirect("event_detail", event_id=event.id)

@staff_required
@require_POST
def award_points(request, activity_id):
    activity = get_object_or_404(Activity.objects.select_related("event"), pk=activity_id, event__host=request.user, event__is_finished=False)
    participant = get_object_or_404(activity.event.participants, pk=request.POST.get("participant_id"))
    try:
        points = int(request.POST.get("points", ""))
    except ValueError:
        points = -1
    if 0 <= points <= 10000:
        ScoreEntry.objects.create(activity=activity, participant=participant, points=points, awarded_by=request.user)
        messages.success(request, f"{participant.nickname}: +{points} очков.")
    else:
        messages.error(request, "Введите целое число очков от 0 до 10000.")
    return redirect("event_detail", event_id=activity.event_id)

@staff_required
@require_POST
def finish_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id, host=request.user)
    if event.is_finished:
        messages.info(request, "Событие уже завершено.")
        return redirect("event_detail", event_id=event.id)
    if request.POST.get("confirm_text", "").strip().casefold() != "ЗАВЕРШИТЬ".casefold() or request.POST.get("confirm_winner") != "yes":
        messages.error(request, "Для подтверждения введите ЗАВЕРШИТЬ и отметьте согласие с итогами.")
        return redirect("event_detail", event_id=event.id)
    event.is_finished = True; event.is_active = False; event.save(update_fields=["is_finished", "is_active"])
    messages.success(request, "Итоги зафиксированы. Победитель отображается в таблице результатов.")
    return redirect("event_detail", event_id=event.id)
