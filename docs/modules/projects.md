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
| `is_featured` | BooleanField | Whether to show on the homepage. |
| `order` | IntegerField | Display order. |
| `tags` | ManyToMany | Relation to `Tag` model. |

### Tag

Represents technologies used in the project (e.g., "React Native", "Python").

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Name of the technology. |

## Integration

- **Homepage**: Featured projects are displayed in the "Work" section of `home.html`.
- **Cards** (homepage and `/projects/`) share `projects/_tags.html` and `projects/_links.html`:
  tags come from the database, and every filled link is shown, plus “Details →” to the project page.
  Title and image also lead to the project page.
- **Admin**: Managed via the Django Admin interface using `unfold`.
