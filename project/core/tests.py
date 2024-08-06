# from django.test import TestCase
# from .models import Project, Testimonial
# from django.core.exceptions import ValidationError

# class ProjectMinimumRequirements(TestCase):
#     def test_project_creation_dosent_require_image(self):
#         project = Project.objects.create(
#             customer="some one",
#             customer_commercial_field="does some stuff",
#             description="some description"
#         )
#         self.assertIsInstance(project, Project)

# class ProjectImageFieldValidation(TestCase):
#     def setUp(self):
#         Project.objects.create(
#             customer="some one",
#             customer_commercial_field="does some stuff",
#             description="some description"
#         )

#     def test_project_creation_cannot_be_published_without_image(self):
#         project = Project.objects.first()
#         self.assertEquals(project.status, Project.Status.EDITING)

#         with self.assertRaises(ValidationError) as e: 
#             project.publish()

#         self.assertIn('image', e.exception.message_dict)
#         self.assertEqual(
#             e.exception.message_dict['image'],
#             ["For publishing you need to add an image."]
#         )

#     def test_project_creation_can_be_publishing_when_has_image(self):
#         project = Project.objects.first()
#         self.assertEquals(project.status, Project.Status.EDITING)

#         project.image = "the/path/to/some/image.jpg"
#         project.publish()
#         self.assertEquals(project.status, Project.Status.PUBLISHED)


# class TestimonialImageFieldValidation(TestCase):
#     def setUp(self):
#         Testimonial.objects.create(
#             name="some one",
#             profession="does some stuff",
#             message="some description"
#         )

#     def test_testimonial_creation_cannot_be_published_without_image(self):
#         testimonial = Testimonial.objects.first()
#         self.assertEquals(testimonial.status, Testimonial.Status.EDITING)

#         with self.assertRaises(ValidationError) as e: 
#             testimonial.publish()

#         self.assertIn('image', e.exception.message_dict)
#         self.assertEqual(
#             e.exception.message_dict['image'],
#             ["For publishing you need to add an image."]
#         )

#     def test_testimonial_creation_can_be_publishing_when_has_image(self):
#         testimonial = Testimonial.objects.first()
#         self.assertEquals(testimonial.status, Testimonial.Status.EDITING)

#         testimonial.image = "the/path/to/some/image.jpg"
#         testimonial.publish()
#         self.assertEquals(testimonial.status, Testimonial.Status.PUBLISHED)
