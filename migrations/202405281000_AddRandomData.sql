-- migrate:up

insert into hotel.hotels (name, address, rating)
select
    name[1 + floor((random() * array_length(name, 1)))::int] || ' ' || substr(md5(random()::text), 1, 5),
    address[1 + floor((random() * array_length(address, 1)))::int] || ' ' || substr(md5(random()::text), 1, 5),
    round((random() * 5)::numeric, 1)
from generate_series(1, 10000) as id
cross join
    (select
        '{Луксури Палас,Эксклюзив,Монарх,Зимний,Березка,Хилтон,ГрандПри,Космос,Огонёк,Мечта,Лагуна,Домино,Аура,Маяк}'
        ::text[] as name,
        '{Иваново,Смирновка,Кузнецовка,Ленина,Гагарина,Балканская,Чехова,Ломоносова,Славы,Космонавтов,Морозов,Будапештсткая}'
        ::text[] as address) as name_address;

-- migrate:down