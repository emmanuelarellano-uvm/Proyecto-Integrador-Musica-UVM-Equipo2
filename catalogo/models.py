from django.db import models


class Usuario(models.Model):
    """Tabla de usuarios: ID, nombre, correo electronico, contrasena y fecha de nacimiento."""
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, verbose_name="Nombre completo")
    correo_electronico = models.EmailField(unique=True, verbose_name="Correo electronico")
    contrasena = models.CharField(max_length=128, verbose_name="Contrasena")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre} ({self.correo_electronico})"


class Artista(models.Model):
    """Tabla de artistas: ID, nombre y genero."""
    id_artista = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del artista")
    genero = models.CharField(max_length=100, default="General", verbose_name="Genero musical")

    class Meta:
        db_table = "artistas"
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"

    def __str__(self):
        return self.nombre


class Album(models.Model):
    """Tabla de albumes: ID, clave foranea a Artista, nombre y fecha de lanzamiento."""
    id_album = models.AutoField(primary_key=True)
    artista = models.ForeignKey(
        Artista,
        on_delete=models.CASCADE,
        related_name="albumes",
        db_column="id_artista",
        verbose_name="Artista",
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del album")
    fecha_lanzamiento = models.CharField(max_length=100, blank=True, default="Sin fecha", verbose_name="Fecha de lanzamiento")

    class Meta:
        db_table = "albumes"
        verbose_name = "Album"
        verbose_name_plural = "Albumes"

    def __str__(self):
        return f"{self.nombre} - {self.artista.nombre}"


class Pista(models.Model):
    """Tabla de pistas: ID, clave foranea a Album, nombre, duracion, ruta y metadatos del CSV."""
    id_pista = models.AutoField(primary_key=True)
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="pistas",
        db_column="id_album",
        verbose_name="Album",
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la pista")
    duracion = models.CharField(max_length=20, default="03:30", verbose_name="Duracion (MM:SS)")
    ruta = models.CharField(max_length=300, blank=True, default="", verbose_name="Ruta del archivo de audio")
    escritores = models.CharField(max_length=255, blank=True, default="No especificado", verbose_name="Escritores")
    productor = models.CharField(max_length=255, blank=True, default="No especificado", verbose_name="Productor")
    racha = models.CharField(max_length=100, blank=True, default="Sin registro", verbose_name="Racha")
    posicion = models.CharField(max_length=100, blank=True, default="Sin posicion", verbose_name="Posicion")
    favorito = models.BooleanField(default=False, verbose_name="Favorito")

    class Meta:
        db_table = "pistas"
        verbose_name = "Pista"
        verbose_name_plural = "Pistas"

    def __str__(self):
        return f"{self.nombre} ({self.album.artista.nombre})"


class ListaReproduccion(models.Model):
    """Tabla de listas de reproduccion: ID, clave foranea a Usuario y nombre."""
    id_lista_reproduccion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="listas_reproduccion",
        db_column="id_usuario",
        verbose_name="Usuario propietario",
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la lista")

    class Meta:
        db_table = "listas_reproduccion"
        verbose_name = "Lista de reproduccion"
        verbose_name_plural = "Listas de reproduccion"

    def __str__(self):
        return f"{self.nombre} ({self.usuario.nombre})"


class ListaReproduccionPista(models.Model):
    """Tabla intermedia Lista de reproduccion - Pista con orden."""
    lista_reproduccion = models.ForeignKey(
        ListaReproduccion,
        on_delete=models.CASCADE,
        related_name="elementos",
        db_column="id_lista_reproduccion",
        verbose_name="Lista de reproduccion",
    )
    pista = models.ForeignKey(
        Pista,
        on_delete=models.CASCADE,
        related_name="en_listas",
        db_column="id_pista",
        verbose_name="Pista",
    )
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden en la lista")

    class Meta:
        db_table = "lista_reproduccion_pista"
        verbose_name = "Pista en lista de reproduccion"
        verbose_name_plural = "Pistas en listas de reproduccion"
        ordering = ["orden"]
        unique_together = ("lista_reproduccion", "pista")

    def __str__(self):
        return f"{self.lista_reproduccion.nombre} #{self.orden}: {self.pista.nombre}"


class Seguidor(models.Model):
    """Tabla de seguidores: relacion muchos a muchos entre Usuario y Artista."""
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="artistas_seguidos",
        db_column="id_usuario",
        verbose_name="Usuario",
    )
    artista = models.ForeignKey(
        Artista,
        on_delete=models.CASCADE,
        related_name="seguidores",
        db_column="id_artista",
        verbose_name="Artista",
    )

    class Meta:
        db_table = "seguidores"
        verbose_name = "Seguidor"
        verbose_name_plural = "Seguidores"
        unique_together = ("usuario", "artista")

    def __str__(self):
        return f"{self.usuario.nombre} sigue a {self.artista.nombre}"
