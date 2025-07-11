import datetime
from pathlib import Path
from skyfield.api import load
from skyfield import almanac


gan_list = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
ji_list = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
month_ji_list = ['인', '묘', '진', '사', '오', '미', '신', '유', '술', '해', '자', '축']


def get_baseDay():
    return datetime.datetime(1900, 1, 1)

# 시주계산
def times_calc(year, month, day, hour, min):
    birth_dt = datetime.datetime(year, month, day, hour, min)
    saju_dt = birth_dt
    
    # 야자시(夜子時) 처리: 23:30 ~ 23:59 사이는 다음날의 자시로 본다.
    if hour == 23 and min >= 30:
        saju_dt += datetime.timedelta(days=1)

    # 일주 정보 가져오기
    day_info = days_calc(saju_dt.year, saju_dt.month, saju_dt.day)
    day_gan_idx = gan_list.index(day_info['gan'])

    # 시간 지지(ji) 계산
    time_ji_idx = -1
    if (hour == 23 and min >= 30) or (hour < 1 or (hour == 1 and min < 30)):
        time_ji_idx = 0 # 자시
    elif hour < 3 or (hour == 3 and min < 30):
        time_ji_idx = 1 # 축시
    elif hour < 5 or (hour == 5 and min < 30):
        time_ji_idx = 2 # 인시
    elif hour < 7 or (hour == 7 and min < 30):
        time_ji_idx = 3 # 묘시
    elif hour < 9 or (hour == 9 and min < 30):
        time_ji_idx = 4 # 진시
    elif hour < 11 or (hour == 11 and min < 30):
        time_ji_idx = 5 # 사시
    elif hour < 13 or (hour == 13 and min < 30):
        time_ji_idx = 6 # 오시
    elif hour < 15 or (hour == 15 and min < 30):
        time_ji_idx = 7 # 미시
    elif hour < 17 or (hour == 17 and min < 30):
        time_ji_idx = 8 # 신시
    elif hour < 19 or (hour == 19 and min < 30):
        time_ji_idx = 9 # 유시
    elif hour < 21 or (hour == 21 and min < 30):
        time_ji_idx = 10 # 술시
    elif hour < 23 or (hour == 23 and min < 30):
        time_ji_idx = 11 # 해시

    # 시간 천간(gan) 계산 (시두법)
    start_gan_idx = (day_gan_idx % 5) * 2
    time_gan_idx = (start_gan_idx + time_ji_idx) % 10

    return {'gan': gan_list[time_gan_idx], 'ji': ji_list[time_ji_idx]}

# 일주계산
def days_calc(year, month, day):
    # 기준일 1900-01-01은 경자일(37번째, index 36)
    baseDay = get_baseDay()
    birth = datetime.datetime(year, month, day)
    deltaDay = (birth - baseDay).days
    cycleDay = (deltaDay + 36) % 60
    gan_idx = cycleDay % 10
    ji_idx = cycleDay % 12
    return {'gan': gan_list[gan_idx], 'ji': ji_list[ji_idx]}

# 12절기 시간 얻기
def get_solar_term_datetimes(year):
    ts = load.timescale()
    data_path = Path(__file__).parent.parent / 'data' / 'de442.bsp'
    eph = load(data_path)
    
    # 12 절기 (월의 시작) longitudes, 입춘부터 순서대로
    longitudes = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
    
    # 검색 범위를 해당 년도 1월 1일 ~ 다음해 1월 31일로 넉넉하게 잡는다
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year + 1, 1, 31)

    t, y = almanac.find_discrete(t0, t1, almanac.solar_longitude(eph), longitudes)
    
    term_map = {lon: dt.utc_datetime() for lon, dt in zip(y, t)}
    
    # longitudes 순서대로 datetime 객체 리스트를 만들어 반환
    sorted_datetimes = [term_map[lon] for lon in longitudes]
    return sorted_datetimes

# 월주계산
def months_calc(year, month, day, hour, min):
    birth_dt = datetime.datetime(year, month, day, hour, min)
    
    # 1. 기준 년도(saju_year) 정하기
    ipchun_this_year = get_ipchun_datetime(year)
    saju_year = year if birth_dt >= ipchun_this_year else year - 1

    # 2. 기준 년도의 12절기 및 다음해 입춘 시간 구하기
    saju_year_terms = get_solar_term_datetimes(saju_year)
    next_year_ipchun = get_ipchun_datetime(saju_year + 1)

    # 3. 생일이 속한 절기 구간을 찾아 월지(ji) 인덱스 구하기
    ji_idx = -1
    for i in range(12):
        start_term = saju_year_terms[i]
        end_term = saju_year_terms[i+1] if i < 11 else next_year_ipchun
        if start_term <= birth_dt < end_term:
            ji_idx = i
            break
    
    if ji_idx == -1:
        raise ValueError(f"월주를 계산할 수 없습니다. ({saju_year}년 절기 내에서 날짜를 찾지 못함)")

    # 4. 년간(년주의 천간)을 기준으로 월간(월주의 천간) 구하기
    saju_year_gan_idx = (saju_year - 4) % 10
    
    # 년간에 따른 월건(월의 천간) 시작 공식 (두수법)
    start_gan_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}
    start_gan_idx = start_gan_map[saju_year_gan_idx]
    
    gan_idx = (start_gan_idx + ji_idx) % 10
    
    return {'gan': gan_list[gan_idx], 'ji': month_ji_list[ji_idx]}

# 년주계산
def years_calc(year, month, day, hour, min):
    ipchun_dt = get_ipchun_datetime(year)
    birth_dt = datetime.datetime(year, month, day, hour, min)

    saju_year = year
    if birth_dt < ipchun_dt:
        saju_year = year - 1

    gan_idx = (saju_year - 4) % 10
    ji_idx = (saju_year - 4) % 12
    return {'gan': gan_list[gan_idx], 'ji': ji_list[ji_idx]}

# 입춘날짜 얻기
def get_ipchun_datetime(year):
    ts = load.timescale()
    data_path = Path(__file__).parent.parent / 'data' / 'de442.bsp'
    eph = load(data_path)
    sun = eph['sun']
    earth = eph['earth']

    # 입춘은 매년 2월 3~5일 사이 → 이 범위에서 태양 황경 315°를 찾는다
    t0 = ts.utc(year, 2, 3)
    t1 = ts.utc(year, 2, 5)

    def sun_longtitude_degrees(t):
        astrometric = earth.at(t).observe(sun).apparent()
        ecliptic = astrometric.ecliptic_latlon()
        return ecliptic[1].degrees % 360
    
    check_time = t0
    while check_time < t1:
        if sun_longtitude_degrees(check_time) >= 315:
            break
        check_time = ts.utc(check_time.utc_datetime() + datetime.timedelta(minutes=30))

    # 2차: 해당 근처에서 1분 단위로 정밀 탐색
    for i in range(31):
        finer = ts.utc(check_time.utc_datetime() - datetime.timedelta(minutes=i))
        if sun_longtitude_degrees(finer) < 315:
            return ts.utc(finer.utc_datetime() + datetime.timedelta(minutes=1)).utc_datetime()

    raise ValueError(f"{year}년의 입춘 시각을 찾을수 없습니다.")