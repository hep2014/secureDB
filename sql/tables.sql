create table if not exists users (
    id            uuid primary key default gen_random_uuid(),
    email         text unique not null,
    password_hash text not null,
    role          text not null default 'student',
    created_at    timestamp default now()
);
create table if not exists sessions (
    token       uuid primary key default gen_random_uuid(),
    user_id     uuid not null references users(id) on delete cascade,
    created_at  timestamp default now(),
    expires_at  timestamp default (now() + interval '30 days')
);
create table if not exists failed_logins (
    id           bigserial primary key,
    email        text not null,
    attempted_at timestamp default now()
);
