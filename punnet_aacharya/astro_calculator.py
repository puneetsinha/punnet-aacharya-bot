import swisseph as swe
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import math
import logging
from config import LAHIRI_AYANAMSA_2025, PLANETS, NAKSHATRAS

logger = logging.getLogger(__name__)

class AstroCalculator:
    def __init__(self):
        logger.info("Initializing AstroCalculator")
        swe.set_ephe_path()  # Use default ephemeris
        self.tf = TimezoneFinder()
        self.geolocator = Nominatim(user_agent="punnet_aacharya")
        logger.info("AstroCalculator initialized successfully")
        
    def get_coordinates(self, place_name):
        """Get latitude and longitude from place name"""
        logger.info(f"Getting coordinates for place: {place_name}")
        try:
            location = self.geolocator.geocode(place_name)
            if location:
                lat, lon = location.latitude, location.longitude
                logger.info(f"Coordinates found: lat={lat}, lon={lon}")
                return lat, lon
            else:
                logger.error(f"Could not find coordinates for {place_name}")
                raise ValueError(f"Could not find coordinates for {place_name}")
        except Exception as e:
            logger.error(f"Error getting coordinates for {place_name}: {str(e)}")
            raise
    
    def calculate_julian_day(self, date_time, timezone_str):
        """Convert datetime to Julian Day"""
        logger.info(f"Calculating Julian Day for {date_time} in timezone {timezone_str}")
        try:
            tz = pytz.timezone(timezone_str)
            dt_tz = tz.localize(date_time)
            dt_utc = dt_tz.astimezone(pytz.UTC)
            
            year = dt_utc.year
            month = dt_utc.month
            day = dt_utc.day
            hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
            
            jd = swe.julday(year, month, day, hour)
            logger.info(f"Julian Day calculated: {jd}")
            return jd
        except Exception as e:
            logger.error(f"Error calculating Julian Day: {str(e)}")
            raise
    
    def calculate_houses(self, jd, lat, lon):
        """Calculate house cusps using Placidus system"""
        logger.info(f"Calculating houses for JD={jd}, lat={lat}, lon={lon}")
        try:
            houses, ascmc = swe.houses(jd, lat, lon, b'P')
            result = {
                'cusps': houses[:12],
                'asc': ascmc[0],
                'mc': ascmc[1]
            }
            logger.info(f"Houses calculated: ASC={ascmc[0]:.2f}, MC={ascmc[1]:.2f}")
            logger.debug(f"House cusps: {houses[:12]}")
            return result
        except Exception as e:
            logger.error(f"Error calculating houses: {str(e)}")
            raise
    
    def calculate_planetary_positions(self, jd):
        """Calculate positions of all planets"""
        logger.info(f"Calculating planetary positions for JD={jd}")
        positions = {}
        
        # Planet codes in Swiss Ephemeris
        planet_codes = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mars': swe.MARS,
            'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS,
            'Saturn': swe.SATURN,
            'Rahu': swe.TRUE_NODE,  # North Node
        }
        
        try:
            for planet_name, planet_code in planet_codes.items():
                logger.debug(f"Calculating position for {planet_name}")
                pos = swe.calc_ut(jd, planet_code)[0]
                
                # Apply Lahiri Ayanamsa for sidereal positions
                sidereal_pos = pos[0] - self.get_ayanamsa(jd)
                if sidereal_pos < 0:
                    sidereal_pos += 360
                    
                positions[planet_name] = {
                    'longitude': sidereal_pos,
                    'sign': self.get_sign(sidereal_pos),
                    'nakshatra': self.get_nakshatra(sidereal_pos),
                    'house': None  # Will be calculated separately
                }
                logger.debug(f"{planet_name}: {sidereal_pos:.2f}° ({positions[planet_name]['sign']})")
            
            # Calculate Ketu (always opposite to Rahu)
            rahu_pos = positions['Rahu']['longitude']
            ketu_pos = (rahu_pos + 180) % 360
            positions['Ketu'] = {
                'longitude': ketu_pos,
                'sign': self.get_sign(ketu_pos),
                'nakshatra': self.get_nakshatra(ketu_pos),
                'house': None
            }
            logger.debug(f"Ketu: {ketu_pos:.2f}° ({positions['Ketu']['sign']})")
            
            logger.info(f"Planetary positions calculated for {len(positions)} planets")
            return positions
            
        except Exception as e:
            logger.error(f"Error calculating planetary positions: {str(e)}")
            raise
    
    def get_ayanamsa(self, jd):
        """Get Lahiri Ayanamsa for given Julian Day"""
        logger.debug(f"Getting Ayanamsa for JD={jd}")
        # This is a simplified calculation
        # In production, use swe.get_ayanamsa_ut()
        return LAHIRI_AYANAMSA_2025
    
    def get_sign(self, longitude):
        """Get zodiac sign from longitude"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign = signs[int(longitude / 30)]
        logger.debug(f"Longitude {longitude:.2f}° corresponds to sign: {sign}")
        return sign
    
    def get_nakshatra(self, longitude):
        """Get nakshatra from longitude"""
        nakshatra_index = int(longitude / 13.333333)
        pada = int((longitude % 13.333333) / 3.333333) + 1
        nakshatra = {
            'name': NAKSHATRAS[nakshatra_index],
            'pada': pada
        }
        logger.debug(f"Longitude {longitude:.2f}° corresponds to nakshatra: {nakshatra['name']} pada {pada}")
        return nakshatra
    
    def calculate_divisional_charts(self, positions):
        """Calculate D9 (Navamsa) and D10 (Dasamsa) charts"""
        logger.info("Calculating divisional charts (D9 and D10)")
        divisional_charts = {
            'D9': {},  # Navamsa for marriage
            'D10': {}  # Dasamsa for career
        }
        
        try:
            for planet, data in positions.items():
                longitude = data['longitude']
                
                # D9 Calculation (each sign divided into 9 parts)
                d9_longitude = (longitude * 9) % 360
                divisional_charts['D9'][planet] = {
                    'longitude': d9_longitude,
                    'sign': self.get_sign(d9_longitude)
                }
                
                # D10 Calculation (each sign divided into 10 parts)
                d10_longitude = (longitude * 10) % 360
                divisional_charts['D10'][planet] = {
                    'longitude': d10_longitude,
                    'sign': self.get_sign(d10_longitude)
                }
                
                logger.debug(f"{planet} D9: {d9_longitude:.2f}° ({divisional_charts['D9'][planet]['sign']})")
                logger.debug(f"{planet} D10: {d10_longitude:.2f}° ({divisional_charts['D10'][planet]['sign']})")
            
            logger.info("Divisional charts calculated successfully")
            return divisional_charts
            
        except Exception as e:
            logger.error(f"Error calculating divisional charts: {str(e)}")
            raise
    
    def calculate_dasha_periods(self, moon_longitude):
        """Calculate Vimshottari Dasha periods based on Moon's position"""
        logger.info(f"Calculating dasha periods for Moon longitude: {moon_longitude:.2f}°")
        
        try:
            # Get birth nakshatra
            nakshatra_index = int(moon_longitude / 13.333333)
            
            # Dasha lords in order
            dasha_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
                          'Jupiter', 'Saturn', 'Mercury']
            dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
            
            # Starting dasha based on nakshatra
            start_index = nakshatra_index % 9
            
            # Calculate elapsed portion of current dasha
            nakshatra_portion = (moon_longitude % 13.333333) / 13.333333
            elapsed_years = dasha_years[start_index] * nakshatra_portion
            
            result = {
                'current_dasha': dasha_lords[start_index],
                'elapsed_years': elapsed_years,
                'remaining_years': dasha_years[start_index] - elapsed_years,
                'sequence': [(dasha_lords[(start_index + i) % 9], dasha_years[(start_index + i) % 9]) 
                            for i in range(9)]
            }
            
            logger.info(f"Current dasha: {result['current_dasha']} ({elapsed_years:.1f} years elapsed, {result['remaining_years']:.1f} remaining)")
            logger.debug(f"Dasha sequence: {result['sequence']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating dasha periods: {str(e)}")
            raise
    
    def generate_birth_chart(self, name, birth_date, birth_time, birth_place):
        """Generate complete birth chart"""
        logger.info(f"Generating birth chart for {name} - {birth_date} {birth_time} at {birth_place}")
        
        try:
            # Get coordinates
            logger.info("Step 1: Getting coordinates")
            lat, lon = self.get_coordinates(birth_place)
            
            # Get timezone
            logger.info("Step 2: Getting timezone")
            timezone_str = self.tf.timezone_at(lat=lat, lng=lon)
            logger.info(f"Timezone: {timezone_str}")
            
            # Combine date and time
            birth_datetime = datetime.combine(birth_date, birth_time)
            
            # Calculate Julian Day
            logger.info("Step 3: Calculating Julian Day")
            jd = self.calculate_julian_day(birth_datetime, timezone_str)
            
            # Calculate houses
            logger.info("Step 4: Calculating houses")
            houses = self.calculate_houses(jd, lat, lon)
            
            # Calculate planetary positions
            logger.info("Step 5: Calculating planetary positions")
            positions = self.calculate_planetary_positions(jd)
            
            # Assign planets to houses
            logger.info("Step 6: Assigning planets to houses")
            for planet, data in positions.items():
                for i, cusp in enumerate(houses['cusps']):
                    next_cusp = houses['cusps'][(i + 1) % 12]
                    if next_cusp < cusp:  # Handle 360-0 boundary
                        if data['longitude'] >= cusp or data['longitude'] < next_cusp:
                            data['house'] = i + 1
                            break
                    else:
                        if cusp <= data['longitude'] < next_cusp:
                            data['house'] = i + 1
                            break
                logger.debug(f"{planet} assigned to house {data['house']}")
            
            # Calculate divisional charts
            logger.info("Step 7: Calculating divisional charts")
            divisional_charts = self.calculate_divisional_charts(positions)
            
            # Calculate dasha periods
            logger.info("Step 8: Calculating dasha periods")
            dasha = self.calculate_dasha_periods(positions['Moon']['longitude'])
            
            result = {
                'name': name,
                'birth_date': birth_date.isoformat(),
                'birth_time': birth_time.isoformat(),
                'birth_place': birth_place,
                'coordinates': {'latitude': lat, 'longitude': lon},
                'timezone': timezone_str,
                'houses': houses,
                'planets': positions,
                'divisional_charts': divisional_charts,
                'dasha': dasha,
                'ascendant_sign': self.get_sign(houses['asc']),
                'sun_sign': positions['Sun']['sign'],
                'moon_sign': positions['Moon']['sign']
            }
            
            logger.info(f"Birth chart generated successfully for {name}")
            logger.info(f"Ascendant: {result['ascendant_sign']}")
            logger.info(f"Current dasha: {dasha['current_dasha']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating birth chart: {str(e)}")
            raise Exception(f"Error calculating birth chart: {str(e)}") 