export function allocateSeats(attendees, capacity) {
  const ordered = [...attendees].sort(
    (a, b) => Number(b.priority === 'vip') - Number(a.priority === 'vip')
  );
  const confirmed = ordered.slice(0, capacity);
  return {
    capacity,
    confirmed,
    waitlist: ordered.slice(capacity),
    seatsRemaining: capacity - confirmed.length,
    totalRequests: attendees.length
  };
}
