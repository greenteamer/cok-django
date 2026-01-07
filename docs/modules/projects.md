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
| `external_link` | URLField | Link to the live project or repo. |
| `case_study_link` | URLField | Link to a detailed case study (internal or external). |
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
- **Admin**: Managed via the Django Admin interface using `unfold`.
