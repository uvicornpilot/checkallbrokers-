from .models import SiteSettings, ContactInfo, AboutUs, OurMission, OurTeam, OurValues


def site_settings(request):
    """Додає налаштування сайту до контексту всіх сторінок"""
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_info': ContactInfo.objects.first(),
        'about_us': AboutUs.objects.first(),
        'our_mission': OurMission.objects.all(),
        'our_team': OurTeam.objects.all(),
        'our_values': OurValues.objects.all()
    } 