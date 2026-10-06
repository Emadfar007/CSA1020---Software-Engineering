const buses = [
  { id: 'rajdhani', name: 'Rajdhani Express', rating: 4.8, departure: '07:30', arrival: '14:00', duration: '6h 30m', type: 'AC Sleeper', tags: ['ac', 'sleeper', 'early'], price: 850, seats: 18 },
  { id: 'greenline', name: 'GreenLine Travels', rating: 4.6, departure: '09:00', arrival: '15:20', duration: '6h 20m', type: 'AC Seater', tags: ['ac', 'seater', 'morning'], price: 720, seats: 11 },
  { id: 'kaveri', name: 'Kaveri Express', rating: 4.4, departure: '11:15', arrival: '17:45', duration: '6h 30m', type: 'Non-AC Sleeper', tags: ['sleeper', 'morning'], price: 590, seats: 24 }
];

const state = {
  step: 0,
  from: 'Bengaluru',
  to: 'Mysuru',
  date: '2026-10-18',
  passengers: 1,
  bus: buses[0],
  selectedSeats: new Set(['2A', '2B']),
  bookedSeats: new Set(['1B', '3D', '5A', '6C']),
  pnr: 'SB8K29Q'
};

const views = ['search', 'results', 'seats', 'confirmed'];
const titles = ['Find your next bus', 'Choose your bus', 'Select your seats', 'Booking confirmed'];
const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);
const friendlyDate = value => new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(`${value}T12:00:00`));

function showToast(message) {
  const toast = document.querySelector('.toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove('show'), 2600);
}

function setStep(step) {
  state.step = step;
  document.querySelectorAll('.view').forEach((view, index) => view.classList.toggle('active', index === step));
  document.querySelectorAll('.stepper li').forEach((item, index) => {
    item.classList.toggle('active', index === step);
    item.classList.toggle('complete', index < step);
  });
  document.querySelector('#page-title').textContent = titles[step];
  document.querySelector('#step-count').textContent = step === 3 ? 'Completed' : `Step ${step + 1} of 4`;
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelector(`[data-nav="${step === 3 ? 'bookings' : 'search'}"]`)?.classList.add('active');
  location.hash = views[step];
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function syncRoute() {
  document.querySelectorAll('.route-from').forEach(el => el.textContent = state.from);
  document.querySelectorAll('.route-to').forEach(el => el.textContent = state.to);
  document.querySelectorAll('.route-date').forEach(el => el.textContent = `${friendlyDate(state.date)} · ${state.passengers} passenger${state.passengers > 1 ? 's' : ''}`);
}

function busCard(bus, featured) {
  return `<article class="bus-card card ${featured ? 'featured' : ''}" data-tags="${bus.tags.join(' ')}">
    <div class="operator"><h3>${bus.name}</h3><span class="rating">★ ${bus.rating}</span></div>
    <div class="timing"><div><strong>${bus.departure}</strong><small>${state.from}</small></div><span>${bus.duration}</span><div><strong>${bus.arrival}</strong><small>${state.to}</small></div></div>
    <div class="bus-meta"><span class="bus-type">${bus.type}</span><small class="seats-left">${bus.seats} seats left</small></div>
    <div class="price"><strong>${money(bus.price)}</strong><small>per seat</small><button class="button ${featured ? 'primary' : 'outline'}" type="button" data-select-bus="${bus.id}">${featured ? 'Select seats' : 'View seats'}</button></div>
  </article>`;
}

function renderBuses() {
  const typeFilters = [...document.querySelectorAll('input[name="type"]:checked')].map(el => el.value);
  const timeFilters = [...document.querySelectorAll('input[name="time"]:checked')].map(el => el.value);
  const matches = buses.filter(bus => (!typeFilters.length || typeFilters.some(tag => bus.tags.includes(tag))) && (!timeFilters.length || timeFilters.some(tag => bus.tags.includes(tag))));
  const sort = document.querySelector('#sort-buses').value;
  matches.sort((a, b) => sort === 'price' ? a.price - b.price : sort === 'rating' ? b.rating - a.rating : buses.indexOf(a) - buses.indexOf(b));
  document.querySelector('#bus-list').innerHTML = matches.map((bus, i) => busCard(bus, i === 0)).join('');
  document.querySelector('#result-count').textContent = matches.length;
  document.querySelector('#empty-results').hidden = matches.length !== 0;
}

function renderSeats() {
  const grid = document.querySelector('#seat-grid');
  grid.innerHTML = '';
  for (let row = 1; row <= 6; row += 1) {
    for (const letter of ['A', 'B', 'C', 'D']) {
      const code = `${row}${letter}`;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `seat${state.selectedSeats.has(code) ? ' selected' : ''}`;
      button.textContent = code;
      button.dataset.seat = code;
      button.disabled = state.bookedSeats.has(code);
      button.setAttribute('aria-label', `Seat ${code}${button.disabled ? ', booked' : state.selectedSeats.has(code) ? ', selected' : ', available'}`);
      button.setAttribute('aria-pressed', String(state.selectedSeats.has(code)));
      grid.append(button);
    }
  }
  updateSummary();
}

function updateSummary() {
  const seats = [...state.selectedSeats].sort();
  const total = seats.length * state.bus.price;
  document.querySelector('#selected-seat-pills').innerHTML = seats.length ? seats.map(seat => `<span>${seat}</span>`).join('') : '<em>No seats selected</em>';
  document.querySelector('#seat-count').textContent = seats.length;
  document.querySelector('#seat-fare').textContent = money(total);
  document.querySelector('#total-fare').textContent = money(total);
  document.querySelector('#continue-payment').disabled = seats.length === 0;
  document.querySelector('#continue-payment').textContent = seats.length ? 'Continue to payment' : 'Select a seat to continue';
}

function selectBus(id) {
  state.bus = buses.find(bus => bus.id === id) || buses[0];
  state.selectedSeats = new Set(['2A', '2B']);
  document.querySelector('#selected-bus-meta').textContent = `${state.bus.name} · ${state.bus.type} · ${state.bus.departure}`;
  document.querySelector('#summary-operator').textContent = state.bus.name;
  document.querySelector('#summary-type').textContent = state.bus.type;
  document.querySelector('#summary-date').textContent = `${friendlyDate(state.date)} · ${state.bus.departure}`;
  renderSeats();
  setStep(2);
}

function confirmBooking() {
  if (!state.selectedSeats.size) return showToast('Choose at least one available seat.');
  const seats = [...state.selectedSeats].sort();
  const total = seats.length * state.bus.price;
  document.querySelector('#ticket-date').textContent = friendlyDate(state.date);
  document.querySelector('#ticket-time').textContent = state.bus.departure;
  document.querySelector('#ticket-seats').textContent = seats.join(', ');
  document.querySelector('#ticket-bus').textContent = state.bus.name;
  document.querySelector('#ticket-total').textContent = money(total);
  document.querySelector('#pnr-code').textContent = state.pnr;
  setStep(3);
}

function downloadTicket() {
  const seats = [...state.selectedSeats].sort().join(', ');
  const contents = `SWIFTBUS E-TICKET\nStatus: CONFIRMED\nPNR: ${state.pnr}\nRoute: ${state.from} to ${state.to}\nDate: ${friendlyDate(state.date)}\nDeparture: ${state.bus.departure}\nBus: ${state.bus.name}\nSeats: ${seats}\nAmount: ${money(state.selectedSeats.size * state.bus.price)}\n`;
  const url = URL.createObjectURL(new Blob([contents], { type: 'text/plain' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `SwiftBus-${state.pnr}.txt`;
  link.click();
  URL.revokeObjectURL(url);
  showToast('Ticket downloaded.');
}

document.querySelector('#search-form').addEventListener('submit', event => {
  event.preventDefault();
  state.from = document.querySelector('#from-city').value;
  state.to = document.querySelector('#to-city').value;
  state.date = document.querySelector('#travel-date').value;
  state.passengers = Number(document.querySelector('#passengers').value);
  if (state.from === state.to) return showToast('Choose different departure and destination cities.');
  syncRoute();
  renderBuses();
  setStep(1);
});

document.addEventListener('click', event => {
  const route = event.target.closest('[data-route]');
  if (route) {
    const [from, to] = route.dataset.route.split('|');
    document.querySelector('#from-city').value = from;
    document.querySelector('#to-city').value = to;
    document.querySelector('#search-form').requestSubmit();
  }
  const busButton = event.target.closest('[data-select-bus]');
  if (busButton) selectBus(busButton.dataset.selectBus);
  const backButton = event.target.closest('[data-back]');
  if (backButton) setStep(Number(backButton.dataset.back));
  const seat = event.target.closest('[data-seat]');
  if (seat && !seat.disabled) {
    state.selectedSeats.has(seat.dataset.seat) ? state.selectedSeats.delete(seat.dataset.seat) : state.selectedSeats.add(seat.dataset.seat);
    renderSeats();
  }
  const toastButton = event.target.closest('[data-toast]');
  if (toastButton) showToast(toastButton.dataset.toast);
  const nav = event.target.closest('[data-nav]');
  if (nav?.dataset.nav === 'search') setStep(0);
  if (nav?.dataset.nav === 'bookings') state.step === 3 ? setStep(3) : showToast('Complete a test booking to view it here.');
});

document.querySelectorAll('.filters input').forEach(input => input.addEventListener('change', renderBuses));
document.querySelector('#sort-buses').addEventListener('change', renderBuses);
document.querySelector('#clear-filters').addEventListener('click', () => { document.querySelectorAll('.filters input').forEach(input => input.checked = false); renderBuses(); });
document.querySelector('#reset-empty').addEventListener('click', () => { document.querySelectorAll('.filters input').forEach(input => input.checked = false); renderBuses(); });
document.querySelector('#continue-payment').addEventListener('click', confirmBooking);
document.querySelector('#download-ticket').addEventListener('click', downloadTicket);
document.querySelector('#book-another').addEventListener('click', () => setStep(0));
document.querySelector('#search-again').addEventListener('click', () => document.querySelector('#search-form').requestSubmit());
document.querySelector('.menu-button').addEventListener('click', event => {
  const open = document.querySelector('.sidebar').classList.toggle('open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});

syncRoute();
renderBuses();
renderSeats();
if (views.includes(location.hash.slice(1))) setStep(views.indexOf(location.hash.slice(1)));
