export function allocateSeats(attendees, capacity) {
  const confirmed = attendees.slice(0, capacity);
  return {
    capacity,
    confirmed,
    waitlist: [],
    seatsRemaining: capacity - confirmed.length,
    totalRequests: attendees.length
  };
}
