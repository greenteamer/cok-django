# Projects Module

The Projects module manages the portfolio projects displayed on the homepage and potentially other sections of the website.

## Responsibility

- Managing project entries (title, description, imagery, links).
- Managing technologies/tags associated with projects.
- Providing project data to views.

## Models

### Project

The core model representing a portfolio project.

| Field | Type | Description |
|-------|------|-------------|
| `title` | CharField | Name of the project. |
| `slug` | SlugField | URL-friendly identifier. |
| `description` | TextField | Short description displayed on cards. |
| `image` | ImageField | Project screenshot or mockup. |
| `live_url` | URLField | The running product: App Store page, website or demo. Shown as “Live ↗”. |
| `source_url` | URLField | Source code repository. Shown as “Source ↗”. |
| `case_study_url` | URLField | A write-up about the project (article or blog post). Shown as “Case study ↗”. |
| `is_featured` | BooleanField | Whether to show on the homepage (hero + "Work" section). |
| `order` | IntegerField | Display order (lower first). On the homepage also decides which covers appear in the hero fan. |
| `tags` | ManyToMany | Relation to `Tag` model. |

### Tag

Represents technologies used in the project (e.g., "React Native", "Python").

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Name of the technology. |

## Integration

- **Homepage**: Featured projects (`is_featured=True`, ordered by `order`) are used in three places of `home.html`:
  - **Hero fan** (`.HeroWork`): `image` of the **first 3** featured projects, each linking to its project page.
    To change which covers are shown, change `order` in the admin. Images are expected in phone
    portrait format (~9:19.5, e.g. 1242×2688); other ratios are cropped (`object-fit: cover`).
  - **Hero proof strip** (`.Hero__proof`): titles of **all** featured projects, each linking to its page.
  - **"Work" section**: full project cards.
  - With no featured projects, the hero fan and proof strip are not rendered.
  - Hero copy must not contain unverifiable claims (client names, counts); show only data backed by real projects.
- **Cards** (homepage and `/projects/`) share `projects/_tags.html` and `projects/_links.html`:
  tags come from the database, and every filled link is shown, plus “Details →” to the project page.
  Title and image also lead to the project page.
- **Admin**: Managed via the Django Admin interface using `unfold`.
