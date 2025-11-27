insert into users (id, email, password_hash, role, created_at) values
('a1f4b5c2-6c1e-4b11-92ad-915c72fae101', 'student1@example.com', '$argon2id$v=19$m=65536,t=3,p=4$Z3JhbmRzYWx0MTIzNDU2$sgX2+zDk3lqbNq3h18EBqNnXj0LwVZ7+vkSUmv2Vrmk', 'student', now()),
('b2e6c7d4-73c0-4e2a-bd0d-1e4bb4ea9211', 'student2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c2FsdHlzYWx0MTIzNDU2$4Vb0diq2KQfUUn1BS2GzQ6WB5cmuJL7tYf4v6yRvUxo', 'student', now()),
('c3a7d8e5-8ac1-4a3b-92f0-55dc3afce132', 'teacher1@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c2VjdXJlc2FsdDEyMzQ1Ng$GPCLGJbAxYbFhr3ZPngMPjW2K40VgF1g2r+iGJm6Yio', 'teacher', now()),
('d493e9f6-2cb2-47bc-8aa8-028b1a5df001', 'teacher2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c2FsdDIyMjEyMzQ1Ng$LkD7XqI6U0y8zK2PdPskrDy7x1E0mMTBi3gS58yFgSo', 'teacher', now()),
('e5a4b7f8-9d31-49de-9b56-df82f6217112', 'admin1@example.com',   '$argon2id$v=19$m=65536,t=3,p=4$c2VjdXJlc2FsdDIyMjEy$4hKZBojzJHT8pxGaJSmUsTq9yG7Ht89QDor6fw5FOo8', 'admin', now()),
('f6c5d8a9-0eb4-40f2-97d8-90b0eaec1234', 'user1@example.com',     '$argon2id$v=19$m=65536,t=3,p=4$dGVzdHNlcmlzYWx0MTIz$GW3nZRn4HSn3MVZyBr0zPqoS7f6i6QvgkZSlMKMIUNc', 'student', now()),
('a7d8e9b0-11c5-4c13-bcef-02f7db31a001', 'user2@example.com',     '$argon2id$v=19$m=65536,t=3,p=4$dHdvZHNvbGRzYWx0$0k5IYcWnN5w4r6w1VwpPcH6DPnl++bUJt0LfeCcRjVE', 'student', now()),
('b8e9fa01-22d6-4f37-bad0-12fedc11b002', 'admin2@example.com',    '$argon2id$v=19$m=65536,t=3,p=4$YWRtaW5zYWx0MTIzNDU2$TAG5C/MMC8/PepRrwZbli98HcEcfVxaxGNWz3ruLYBs', 'admin', now());
insert into sessions (token, user_id, created_at, expires_at) values
('11111111-aaaa-bbbb-cccc-000000000001', 'a1f4b5c2-6c1e-4b11-92ad-915c72fae101', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000002', 'b2e6c7d4-73c0-4e2a-bd0d-1e4bb4ea9211', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000003', 'c3a7d8e5-8ac1-4a3b-92f0-55dc3afce132', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000004', 'd493e9f6-2cb2-47bc-8aa8-028b1a5df001', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000005', 'e5a4b7f8-9d31-49de-9b56-df82f6217112', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000006', 'f6c5d8a9-0eb4-40f2-97d8-90b0eaec1234', now(), now() + interval '30 days'),
('11111111-aaaa-bbbb-cccc-000000000007', 'a7d8e9b0-11c5-4c13-bcef-02f7db31a001', now(), now() + interval '30 days');
