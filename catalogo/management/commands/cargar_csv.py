from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from catalogo.models import Album, Artista, Pista


class Command(BaseCommand):
    help = "Carga los registros limpios de U3_Songs_Limpio.csv en la base de datos Django."

    def add_arguments(self, parser):
        parser.add_argument(
            "--archivo",
            type=str,
            default="U3_Songs_Limpio.csv",
            help="Ruta al archivo CSV limpio generado con Pandas.",
        )

    def handle(self, *args, **options):
        ruta = Path(options["archivo"])
        if not ruta.exists():
            self.stderr.write(self.style.ERROR(f"No se encontro el archivo: {ruta}"))
            return

        df = pd.read_csv(ruta, encoding="utf-8-sig")
        creadas = 0

        for _, fila in df.iterrows():
            nombre_artista = str(fila.get("ARTISTA", "Artista desconocido")).strip()
            nombre_album = str(fila.get("ALBUM", "Sin album")).strip()
            fecha_lanz = str(fila.get("LANZAMIENTO", "Sin fecha")).strip()
            nombre_pista = str(fila.get("TITULO", "Sin titulo")).strip()

            artista, _ = Artista.objects.get_or_create(
                nombre=nombre_artista,
                defaults={"genero": "Rock / Pop Clasico"},
            )
            album, _ = Album.objects.get_or_create(
                artista=artista,
                nombre=nombre_album,
                defaults={"fecha_lanzamiento": fecha_lanz},
            )
            _, creada = Pista.objects.get_or_create(
                album=album,
                nombre=nombre_pista,
                defaults={
                    "duracion": "03:30",
                    "ruta": "",
                    "escritores": str(fila.get("ESCRITORES", "No especificado")).strip(),
                    "productor": str(fila.get("PRODUCTOR", "No especificado")).strip(),
                    "racha": str(fila.get("RACHA", "Sin registro")).strip(),
                    "posicion": str(fila.get("POSICION", "Sin posicion")).strip(),
                    "favorito": False,
                },
            )
            if creada:
                creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga completada. Pistas nuevas insertadas: {creadas}. "
                f"Total en base de datos: {Pista.objects.count()}."
            )
        )
