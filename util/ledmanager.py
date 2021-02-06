import RPi.GPIO as GPIO
import util.config as cfg


def red_led_on():
    GPIO.output(cfg.pin["red_led"], GPIO.HIGH)
    GPIO.output(cfg.pin["yellow_led"], GPIO.LOW)
    GPIO.output(cfg.pin["green_led"], GPIO.LOW)


def yellow_led_on():
    GPIO.output(cfg.pin["red_led"], GPIO.LOW)
    GPIO.output(cfg.pin["yellow_led"], GPIO.HIGH)
    GPIO.output(cfg.pin["green_led"], GPIO.LOW)


def green_led_on():
    GPIO.output(cfg.pin["red_led"], GPIO.LOW)
    GPIO.output(cfg.pin["yellow_led"], GPIO.LOW)
    GPIO.output(cfg.pin["green_led"], GPIO.HIGH)
