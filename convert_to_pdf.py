import io
from fpdf import FPDF
from pathlib import Path


class PDF(FPDF):
    def header(self):
        self.image("Fonts/bg.png", x=0, y=0, w=595, h=842)
        pass

    def footer(self):
        pass

    def add_section_text(self, x, y, width, text, font_size=10, bold=False, line_height=13):
        font_style = 'B' if bold else ''
        self.set_font('Roboto', font_style, font_size)
        self.set_xy(x, y)
        self.multi_cell(width, line_height, text, align='L')
        return self.get_y()


class ResumeParser:
    def __init__(self):
        self.sections = {}

    def parse_ai_response(self, response_text):
        """
        Улучшенный парсер AI респонса
        """
        sections = response_text.split('---')
        parsed_data = {}

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.split('\n')
            if not lines:
                continue

            title = lines[0].strip()

            content_lines = lines[1:]
            content = '\n'.join(line.rstrip() for line in content_lines).strip()

            if title == "Опыт работы":
                work_sections = []
                current_company = None
                current_content = []

                for line in content_lines:
                    line = line.strip()
                    if not line:
                        if current_content:
                            current_content.append('')
                        continue

                    if (' - ' in line and
                            ('настоящее время' in line or
                             any(month in line for month in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                                                             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
                                                             'Декабрь']) or
                             any(year in line for year in ['2020', '2021', '2022', '2023', '2024', '2025']))):

                        if current_company:
                            work_sections.append(f"{current_company}\n{chr(10).join(current_content)}")

                        current_company = line
                        current_content = []
                    else:
                        current_content.append(line)


                if current_company:
                    work_sections.append(f"{current_company}\n{chr(10).join(current_content)}")

                if work_sections:

                    work_content = []
                    first_line = content_lines[0].strip() if content_lines else ""
                    if "Общий стаж:" in first_line:
                        work_content.append(first_line)
                        work_content.append("")

                    work_content.extend(work_sections)
                    content = '\n\n'.join(work_content)

            if title and content:
                parsed_data[title] = content

        return parsed_data

    def extract_name_and_position(self, parsed_data):
        """
        Извлекает имя и должность
        """
        name = "Всеволод"  # Из контактной информации видно @VVVsevolodVVV
        position = "Product Owner / Продуктовый аналитик"

        if "Персональные данные" in parsed_data:
            personal = parsed_data["Персональные данные"]
            lines = personal.split('\n')
            if len(lines) >= 2:
                name = lines[0].strip()
                position = lines[1].strip()

        return name, position

    def extract_contact_info(self, parsed_data):
        """
        Извлекает контактную информацию
        """
        contact_info = ""
        if "Контактная информация" in parsed_data:
            contact_info = parsed_data["Контактная информация"]
        elif "Контакты" in parsed_data:
            contact_info = parsed_data["Контакты"]

        return contact_info if contact_info else "Контактная информация не указана"

    def format_work_experience(self, work_text):
        """
        Форматирует секцию "Опыт работы" для лучшего отображения
        """


        lines = work_text.split('\n')
        formatted_lines = []

        for i, line in enumerate(lines):
            if not line.strip():
                formatted_lines.append('')
                continue


            if not line.strip().startswith('•'):

                if formatted_lines and formatted_lines[-1] != '' and i > 0:
                    formatted_lines.append('')
                formatted_lines.append(line.strip())
            else:
                formatted_lines.append(line.strip())

        result = '\n'.join(formatted_lines)

        return result


def clean_text_for_pdf(text):
    """
    Очищает текст от проблемных символов для PDF
    """
    text = text.replace('—', '-').replace('–', '-').replace('−', '-')
    text = text.replace('\u00a0', ' ').replace('\u202f', ' ').replace('\u2009', ' ')
    text = text.replace('\u2000', ' ').replace('\u2001', ' ').replace('\u2002', ' ')
    text = text.replace('\u2003', ' ').replace('\u2004', ' ').replace('\u2005', ' ')
    return text


def create_resume_from_ai_response(ai_response, output_filename="generated_resume.pdf"):
    """
    Создает PDF резюме из AI респонса
    """
    parser = ResumeParser()
    parsed_data = parser.parse_ai_response(ai_response)

    for key, value in parsed_data.items():
        parsed_data[key] = clean_text_for_pdf(value)

    pdf = PDF('P', 'pt', 'A4')
    pdf.add_page()

    pdf.add_font('Roboto', '', 'Fonts/Roboto-Regular.ttf', uni=True)
    pdf.add_font('Roboto', 'B', 'Fonts/Roboto-Bold.ttf', uni=True)

    page_width = 595
    margin_left = 20
    margin_right = 30
    margin_top = 30
    left_column_width = page_width * 0.35 - margin_left
    right_column_width = page_width * 0.6 - margin_right - 20
    left_column_x = margin_left
    right_column_x = margin_left + left_column_width + 20
    section_spacing_l = 20
    section_spacing_r = 10

    current_y_left = margin_top
    current_y_right = margin_top

    # --- ЛЕВАЯ КОЛОНКА ---
    name, position = parser.extract_name_and_position(parsed_data)
    current_y_left = pdf.add_section_text(
        left_column_x, current_y_left, left_column_width,
        f"{name}\n\n{position}",
        font_size=14, bold=True
    ) + section_spacing_l

    left_column_sections = ["Личные качества", "Контактная информация", "Контакты", "Образование",
                            "Дополнительные сведения"]

    for section_name in left_column_sections:
        if section_name in parsed_data:
            current_y_left = pdf.add_section_text(
                left_column_x, current_y_left, left_column_width,
                section_name,
                font_size=12, bold=True
            ) + 5

            current_y_left = pdf.add_section_text(
                left_column_x, current_y_left, left_column_width,
                parsed_data[section_name]
            ) + section_spacing_l

    # --- ПРАВАЯ КОЛОНКА ---
    right_column_sections = ["Опыт работы", "Навыки", "Другие проекты", "Проекты", "Достижения", "Сертификаты"]

    for section_name in right_column_sections:
        if section_name in parsed_data:

            current_y_right = pdf.add_section_text(
                right_column_x, current_y_right, right_column_width,
                section_name,
                font_size=12, bold=True
            ) + 5

            content = parsed_data[section_name]

            if section_name == "Опыт работы":
                content = parser.format_work_experience(content)


            content = content.replace('**', '').replace('*', '')

            lines = content.split('\n')

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                if not line_stripped:
                    current_y_right += 5
                    continue


                is_header = False
                if i == 0:
                    is_header = True
                elif i > 0 and not lines[i - 1].strip():
                    is_header = True
                elif not line_stripped.startswith('•') and not line_stripped.startswith('-'):

                    if (' - ' in line_stripped and
                            ('настоящее время' in line_stripped or
                             any(month in line_stripped for month in
                                 ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь','Июль','Август',
                                  'Сентябрь','Октябрь','Ноябрь','Декабрь']))):
                        is_header = True

                if is_header:
                    current_y_right = pdf.add_section_text(
                        right_column_x, current_y_right, right_column_width,
                        line_stripped, font_size=11, bold=True
                    ) + 3
                else:
                    current_y_right = pdf.add_section_text(
                        right_column_x, current_y_right, right_column_width,
                        line_stripped, font_size=10
                    ) + 2

            current_y_right += section_spacing_r

    pdf_buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    return pdf_buffer, parsed_data