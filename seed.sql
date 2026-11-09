-- A small support queue. Fictional customers, fictional orders.
CREATE TABLE tickets (
    id          INTEGER PRIMARY KEY,
    customer    TEXT NOT NULL,
    subject     TEXT NOT NULL,
    body        TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('open', 'closed')),
    priority    TEXT NOT NULL CHECK (priority IN ('low', 'normal', 'high')),
    created_at  TEXT NOT NULL
);

CREATE TABLE notes (
    id          INTEGER PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets (id),
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

INSERT INTO tickets (id, customer, subject, body, status, priority, created_at) VALUES
(1,  'Ana Ruiz',      'Refund not received',            'I returned order 4471 two weeks ago and the refund still has not arrived.', 'open',   'high',   '2026-10-28'),
(2,  'Ben Carter',    'Cannot log in after reset',      'The password reset link says it expired the moment I open it.',            'open',   'high',   '2026-10-30'),
(3,  'Chloe Martin',  'Wrong size delivered',           'Ordered a medium, received a large. Can I exchange it?',                   'open',   'normal', '2026-11-01'),
(4,  'Diego Fernandez','Charged twice for one order',   'My card shows two charges for order 4520. Please refund the duplicate.',   'open',   'high',   '2026-11-02'),
(5,  'Emma Wilson',   'Change delivery address',        'Can I change the address on order 4533 before it ships?',                  'closed', 'normal', '2026-11-02'),
(6,  'Farid Haddad',  'Invoice for my company',         'I need an invoice with my company tax number for order 4498.',             'open',   'low',    '2026-11-03'),
(7,  'Grace Lee',     'Refund for cancelled order',     'I cancelled order 4540 within an hour. When will the refund show up?',     'open',   'normal', '2026-11-04'),
(8,  'Hugo Silva',    'App crashes on checkout',        'The app closes every time I tap Pay on Android.',                          'open',   'high',   '2026-11-05'),
(9,  'Iris Novak',    'Discount code not applied',      'The code WELCOME10 was accepted but the total did not change.',            'closed', 'low',    '2026-11-05'),
(10, 'Jonas Berg',    'Where is my order?',             'Tracking has not updated in five days for order 4551.',                    'open',   'normal', '2026-11-06'),
(11, 'Kira Tanaka',   'Delete my account',              'Please delete my account and all my data.',                                'open',   'normal', '2026-11-07'),
(12, 'Luca Romano',   'Refund partially missing',       'I was refunded 40 dollars but the item cost 55.',                          'open',   'normal', '2026-11-08');
