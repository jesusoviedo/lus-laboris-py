<div align="center">

**Language / Idioma:**  
[🇺🇸 English](#act---local-github-actions-workflow-runner) | [🇪🇸 Español](#act---ejecutor-local-de-workflows-de-github-actions)

</div>

---

# act - Local GitHub Actions Workflow Runner

## What is act?

**act** is a command-line tool that lets you run your GitHub Actions workflows locally, simulating the GitHub Actions runner environment. It's ideal for debugging and validating your workflows before pushing changes to your repository.

## Installation

### Linux

```bash
sudo apt-get install act
```
Or with Homebrew:
```bash
brew install act
```

### MacOS

```bash
brew install act
```

### Windows

Download the executable from the [act releases page](https://github.com/nektos/act/releases) and add it to your PATH.

## Basic Concepts

- **Workflow**: A YAML file in `.github/workflows/` defining jobs and steps.
- **Job**: A set of steps executed on a runner.
- **Runner**: The environment where jobs run (act uses Docker containers).
- **Secret**: Sensitive variables (like passwords or tokens) used in workflows.
- **Event**: An action that triggers the workflow (push, pull_request, etc).

## Listing Available Jobs

To list jobs defined in your workflows:

```bash
act -l
```

## Running a Workflow/Job

To run all jobs for an event (e.g., push):

```bash
act push
```

To run a specific job:

```bash
act -j job_name
```

You can simulate other events like `pull_request`:

```bash
act pull_request
```

## Configuring Secrets and Environment Variables

### Secrets

1. **Create a secrets file** (can be your `.env` or a `.secrets` file):

   ```
   SECRET_NAME=value
   ANOTHER_SECRET=value2
   ```

2. **Run act using the secrets file**:

   ```bash
   act --secret-file path/to/your.env
   ```

   Secrets will be available in the workflow as `${{ secrets.SECRET_NAME }}`.

### Environment Variables

If you have non-secret environment variables, use:

```bash
act --env-file path/to/your.env
```

These variables will be available as normal environment variables.

## Example

Suppose you have this workflow in `.github/workflows/ci.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Secret is ${{ secrets.MY_SECRET }}"
      - run: echo "Variable is $MY_VARIABLE"
```

And your `.env` file:

```
MY_SECRET=supersecret
MY_VARIABLE=value123
```

To run the workflow locally:

```bash
act --secret-file ../../.env --env-file ../../.env
```

## Useful Tips

- If you use custom Docker images, specify with `-P ubuntu-latest=image`.
- You can pass individual secrets with `-s NAME=value`.
- Use `-v` for verbose output.

## Resources

- [act official repository](https://github.com/nektos/act)
- [GitHub Actions documentation](https://docs.github.com/en/actions)

---

# act - Ejecutor local de Workflows de GitHub Actions

## ¿Qué es act?

**act** es una herramienta de línea de comandos que permite ejecutar y probar los workflows de GitHub Actions en tu máquina local, simulando el entorno de los runners de GitHub. Es ideal para depurar y validar tus flujos antes de hacer push al repositorio.

## Instalación

### Linux

```bash
sudo apt-get install act
```
O con Homebrew:
```bash
brew install act
```

### MacOS

```bash
brew install act
```

### Windows

Descarga el ejecutable desde la [página de releases de act](https://github.com/nektos/act/releases) y agrégalo a tu PATH.

## Conceptos básicos

- **Workflow**: Archivo YAML en `.github/workflows/` que define los jobs y pasos a ejecutar.
- **Job**: Conjunto de pasos que se ejecutan en un runner.
- **Runner**: Entorno donde se ejecutan los jobs (act usa contenedores Docker).
- **Secret**: Variables sensibles (como contraseñas o tokens) que se usan en los workflows.
- **Evento**: Acción que dispara el workflow (push, pull_request, etc).

## Ver los jobs disponibles

Para listar los jobs definidos en tus workflows:

```bash
act -l
```

## Ejecutar un workflow/job

Para ejecutar todos los jobs asociados a un evento (por ejemplo, push):

```bash
act push
```

Para ejecutar un job específico:

```bash
act -j nombre_del_job
```

Puedes simular otros eventos como `pull_request`:

```bash
act pull_request
```

## Configurar secrets y variables de entorno

### Secrets

1. **Crea un archivo de secrets** (puede ser tu `.env` o un archivo llamado `.secrets`):

   ```
   NOMBRE_SECRETO=valor
   OTRO_SECRETO=valor2
   ```

2. **Ejecuta act usando el archivo de secrets**:

   ```bash
   act --secret-file ruta/al/archivo.env
   ```

   Los secrets estarán disponibles en el workflow como `${{ secrets.NOMBRE_SECRETO }}`.

### Variables de entorno

Si tienes variables de entorno que no son secrets, puedes usar:

```bash
act --env-file ruta/al/archivo.env
```

Estas variables estarán disponibles como variables de entorno normales.

## Ejemplo

Supón que tienes este workflow en `.github/workflows/ci.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "El secreto es ${{ secrets.MI_SECRETO }}"
      - run: echo "La variable es $MI_VARIABLE"
```

Y tu archivo `.env`:

```
MI_SECRETO=supersecreto
MI_VARIABLE=valor123
```

Para ejecutar el workflow localmente:

```bash
act --secret-file ../../.env --env-file ../../.env
```

## Consejos útiles

- Si usas imágenes personalizadas de Docker, puedes especificar la imagen con `-P ubuntu-latest=imagen`.
- Puedes pasar secrets individuales con `-s NOMBRE=valor`.
- Usa `-v` para ver la salida en modo detallado (verbose).

## Recursos

- [Repositorio oficial de act](https://github.com/nektos/act)
- [Documentación de GitHub Actions](https://docs.github.com/en/actions)
