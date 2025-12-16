# models.py
from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    InlinePanel,
)
from wagtail.images.models import Image
from wagtail.images.blocks import ImageChooserBlock   # ✅ pour l'image dans chaque destination

# Pour la page contact avec formulaire email
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from modelcluster.fields import ParentalKey

# ============================================================
# 1) Bloc réutilisable pour décrire un destination
#    -> utilisé sur la page d'accueil (aperçu)
#    -> utilisé sur la page "Nos destinations" (liste complète)
#    Chaque destination a maintenant :
#      - un badge/numéro
#      - un titre
#      - une description
#      - une liste de points clés
#      - UNE IMAGE
# ============================================================
class DestinationBlock(blocks.StructBlock):
    """
    Bloc "destination" pour StreamField.
    On pourra en ajouter plusieurs dans l'admin Wagtail.
    """

    badge = blocks.CharBlock(
        required=False,
        help_text="Petit texte au-dessus (ex : 01, 02, 03...)",
        label="Badge / numéro"
    )

    title = blocks.CharBlock(
        required=True,
        max_length=120,
        label="Titre de la destination"
    )

    description = blocks.TextBlock(
        required=False,
        label="Description courte"
    )

    # ✅ Nouvelle image pour chaque destination (illustration moderne)
    image = ImageChooserBlock(
        required=False,
        help_text="Image ou icône illustrant la destination (format horizontal de préférence).",
        label="Image de la destination"
    )

    features = blocks.ListBlock(
        blocks.CharBlock(label="Point clé"),
        required=False,
        label="Liste de points clés (bullet points)"
    )

    class Meta:
        icon = "cog"
        label = "Destination"
        help_text = "Bloc réutilisable pour présenter un destination avec une image."


# ============================================================
# 2) Page d'accueil
#    - hero (image + texte + boutons)
#    - aperçu de 2–3 destinations
# ============================================================
class HomePage(Page):
    # --------- HERO (bandeau principal avec image) ----------
    hero_kicker = models.CharField(
        "Petit texte au-dessus du titre",
        max_length=150,
        blank=True,
        default="Bienvenue",  # ✅ default pour éviter la question en migration
        help_text="Ex : 'Agence digitale · Exemple Wagtail'"
    )

    hero_title = models.CharField(
        "Titre principal",
        max_length=200,
        default="Titre de la page d’accueil",  # ✅ default
        help_text="Ex : 'Créez un site vitrine moderne, clair et efficace.'"
    )

    hero_subtitle = models.TextField(
        "Texte sous le titre",
        blank=True,
        default="Sous-titre de présentation pour la page d’accueil.",  # ✅ default
        help_text="Quelques phrases qui expliquent le site."
    )

    # Image de fond du hero (choisie dans la bibliothèque d'images Wagtail)
    hero_background_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image de fond du hero",
        help_text="Grande image plein écran affichée en haut de la page."
    )

    # Bouton principal -> généralement la page “À propos”
    hero_primary_button_text = models.CharField(
        "Texte du bouton principal",
        max_length=50,
        default="En savoir plus sur nous",
    )
    hero_primary_button_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Page du bouton principal",
        help_text="Page vers laquelle le bouton principal redirige (ex : À propos).",
    )

    # Bouton secondaire -> généralement la page “Contact”
    hero_secondary_button_text = models.CharField(
        "Texte du bouton secondaire",
        max_length=50,
        default="Discutons de votre projet",
        blank=True,
    )
    hero_secondary_button_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Page du bouton secondaire",
        help_text="Page vers laquelle le bouton secondaire redirige (ex : Contact).",
    )

    # --------- SECTION "APERÇU DES DestinationS" ----------
    destinations_preview_title = models.CharField(
        "Titre de la section destinations (accueil)",
        max_length=150,
        default="Nos destinations",
    )

    destinations_preview_intro = models.TextField(
        "Texte d’intro de la section destinations (accueil)",
        blank=True,
        default="Un aperçu rapide de nos destinations.",  # ✅ default
        help_text="Petite phrase pour introduire les destinations."
    )

    # StreamField utilisant notre bloc DestinationBlock (avec image)
    destinations_preview = StreamField(
        [
            ("destination", DestinationBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name="Destinations à afficher sur l’accueil (aperçu)",
        #help_text="Liste de 2–3 destinations pour la page d’accueil.",
    )

    # --------- PANELS POUR L'ADMIN WAGTAIL ----------
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_kicker"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_background_image"),
                FieldPanel("hero_primary_button_text"),
                PageChooserPanel("hero_primary_button_page"),
                FieldPanel("hero_secondary_button_text"),
                PageChooserPanel("hero_secondary_button_page"),
            ],
            heading="Section hero (bandeau principal)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("destinations_preview_title"),
                FieldPanel("destinations_preview_intro"),
                FieldPanel("destinations_preview"),
            ],
            heading="Aperçu des destinations sur la page d’accueil",
        ),
    ]


# ============================================================
# 3) Page "Nos destinations"
#    - même bloc DestinationBlock, mais pour la liste complète
# ============================================================
class DestinationsPage(Page):
    intro_title = models.CharField(
        "Titre principal",
        max_length=150,
        default="Nos destinations",
    )

    intro_subtitle = models.TextField(
        "Texte d’intro",
        blank=True,
        default="Voici un exemple de section destinations que vous pouvez adapter.",  # ✅ default
        help_text="Ex : 'Voici un exemple de section destinations...'"
    )

    # On réutilise le même bloc DestinationBlock avec image
    destinations = StreamField(
        [
            ("destination", DestinationBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name="Destinations",
        help_text="Liste complète des destinations proposés.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro_title"),
        FieldPanel("intro_subtitle"),
        FieldPanel("destinations"),
    ]


# ============================================================
# 4) Page "À propos"
#    - texte de présentation
#    - image + légende
# ============================================================
class AboutPage(Page):
    intro_title = models.CharField(
        "Titre principal",
        max_length=150,
        default="À propos",
    )

    intro_subtitle = models.TextField(
        "Texte d’intro",
        blank=True,
        default="En savoir plus sur nous.",
        help_text="Une petite phrase pour introduire la page."
    )

    body = RichTextField(
        "Texte de présentation",
        blank=True,
        default="",
        help_text="Contenu principal : histoire, mission, valeurs..."
    )

    # 4 images distinctes
    image_1 = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image 1",
    )
    image_2 = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image 2",
    )
    image_3 = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image 3",
    )
    image_4 = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image 4",
    )

    image_caption = models.CharField(
        "Légende des images",
        max_length=255,
        blank=True,
        default="",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro_title"),
        FieldPanel("intro_subtitle"),
        FieldPanel("body"),
        FieldPanel("image_1"),
        FieldPanel("image_2"),
        FieldPanel("image_3"),
        FieldPanel("image_4"),
        FieldPanel("image_caption"),
    ]


# ============================================================
# 5) Champs des formulaires (Wagtail Forms) pour la page Contact
# ============================================================
class FormField(AbstractFormField):
    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )

# ============================================================
# 6) Page "Contact"
#    - titre + intro
#    - coordonnées de contact
#    - texte d’explication au-dessus du formulaire
# ============================================================
class ContactPage(AbstractEmailForm):
    intro_title = models.CharField(
        "Titre principal",
        max_length=150,
        default="Contact",
    )

    intro_subtitle = models.TextField(
        "Texte d’intro",
        blank=True,
        default="Un exemple de page contact avec un formulaire simple.",  # ✅ default
        help_text="Ex : 'Un exemple de page contact avec un formulaire simple.'"
    )

    contact_email = models.EmailField(
        "Email de contact",
        blank=True,
        default="contact@exemple.com",  # ✅ default simple
    )

    contact_phone = models.CharField(
        "Téléphone",
        max_length=50,
        blank=True,
        default="",  # ✅ default vide
    )

    contact_address = models.CharField(
        "Adresse",
        max_length=255,
        blank=True,
        default="Adresse de votre entreprise",  # ✅ default pédagogique
    )

    contact_text = RichTextField(
        "Texte au-dessus du formulaire",
        blank=True,
        default="",  # ✅ default vide
        help_text='Ex : "Utilisez ce formulaire comme base..."'
    )

     # Configuration email (où vont les messages)
    to_address = models.CharField(
        "Adresse email qui recevra les messages",
        max_length=255,
        blank=False,
        default="contact@exemple.com",
        help_text="Les messages du formulaire seront envoyés à cette adresse.",
    )

    from_address = models.CharField(
        "Adresse expéditeur",
        max_length=255,
        default="noreply@monsite.com",
        help_text="Adresse utilisée comme expéditeur des emails.",
    )

    subject = models.CharField(
        "Sujet de l’email",
        max_length=255,
        default="Nouveau message depuis votre site vitrine",
    )

    thank_you_text = RichTextField(
        "Message de remerciement après envoi",
        blank=True,
        default="Merci ! Votre message a bien été envoyé.",
    )


    content_panels = AbstractEmailForm.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("intro_title"),
                FieldPanel("intro_subtitle"),
                FieldPanel("contact_text"),
            ],
            heading="Introduction",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
                FieldPanel("contact_address"),
            ],
            heading="Coordonnées affichées",
        ),
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading="Configuration des emails",
        ),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("thank_you_text"),
    ]

    # Onglet "Submissions" dans l’admin (facultatif mais pratique)
    submissions_panels = [
        FormSubmissionsPanel(),
    ]
# Fin de models.py


