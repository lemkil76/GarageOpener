import time
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    _GPIO_AVAILABLE = True
except ImportError:
    logger.warning("GPIO not available – simulation mode")
    _GPIO_AVAILABLE = False


def setup_pin(pin):
    if _GPIO_AVAILABLE:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)


def pulse_relay(pin, duration_ms):
    if _GPIO_AVAILABLE:
        GPIO.output(pin, GPIO.LOW)
        time.sleep(duration_ms / 1000.0)
        GPIO.output(pin, GPIO.HIGH)
    else:
        logger.info(f"[SIM] pulse_relay pin={pin} duration={duration_ms}ms")


def cleanup():
    if _GPIO_AVAILABLE:
        GPIO.cleanup()
