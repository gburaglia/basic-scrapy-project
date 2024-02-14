import scrapy
from basic_scrapy_spider.items import QuoteItem

alumni_array = [
'linkedinusername1',
'linkedinusername2'
]

class LinkedInPeopleProfileSpider(scrapy.Spider):
    name = "linkedin_people_profile"

    def start_requests(self):
        profile_list = alumni_array
        for profile in profile_list:
            linkedin_people_url = f'https://www.linkedin.com/in/{profile}/'
            yield scrapy.Request(url=linkedin_people_url, callback=self.parse_profile, meta={'profile': profile, 'linkedin_url': linkedin_people_url})

    def parse_profile(self, response):
        item = {}
        item['profile'] = response.meta['profile']
        item['url'] = response.meta['linkedin_url']

        """
            SUMMARY SECTION
        """
        summary_box = response.css("section.top-card-layout")
        item['name'] = summary_box.css("h1::text").get().strip()
        item['description'] = summary_box.css("h2::text").get().strip()
        item['current_company'] = summary_box.css("div.top-card__links-container div:nth-child(1) a::attr(href)").get().strip()

        ## Location
        try:
            item['location'] = summary_box.css('div.profile-info-subheader div:nth-child(1) span:nth-child(1)::text').get().strip()
            # item['location'] = summary_box.css('span.not-first-middot.top-card-layout__first-subline::text').get()
            #main-content > section.core-rail.mx-auto.papabear\:w-core-rail-width.mamabear\:max-w-\[790px\].babybear\:max-w-\[790px\] > div > section > section.top-card-layout.container-lined.overflow-hidden.babybear\:rounded-\[0px\] > div > div.top-card-layout__entity-info-container.flex.flex-wrap.papabear\:flex-nowrap > div:nth-child(1) > h3 > div > div:nth-child(1) > span:nth-child(1)
        except:
            item['location'] = summary_box.css('div.top-card-layout__first-subline::text').get().strip()
            if 'followers' in item['location'] or 'connections' in item['location']:
                item['location'] = ''

        """
            EXPERIENCE SECTION
        """
        item['experience'] = []
        experience_blocks = response.css('li.experience-item')
        for block in experience_blocks:
            experience = {}
            ## organisation profile url
            experience['organisation_profile'] = block.css('h4 a::attr(href)').get(default='').split('?')[0]
                
                
            ## location
            experience['location'] = block.css('p.experience-item__location::text').get(default='').strip()
                
                
            ## description
            try:
                experience['description'] = block.css('p.show-more-less-text__text--more::text').get().strip()
            except Exception as e:
                print('experience --> description', e)
                try:
                    experience['description'] = block.css('p.show-more-less-text__text--less::text').get().strip()
                except Exception as e:
                    print('experience --> description', e)
                    experience['description'] = ''
                    
            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = date_ranges[1]
                    experience['duration'] = block.css('span.date-range__duration::text').get()
                elif len(date_ranges) == 1:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = 'present'
                    experience['duration'] = block.css('span.date-range__duration::text').get()
            except Exception as e:
                print('experience --> time ranges', e)
                experience['start_time'] = ''
                experience['end_time'] = ''
                experience['duration'] = ''
            
            item['experience'].append(experience)
    
        """
            EDUCATION SECTION
        """
        item['education'] = []
        education_blocks = response.css('li.education__list-item')
        for block in education_blocks:
            education = {}

            ## organisation
            education['organisation'] = block.css('h3::text').get(default='').strip()


            ## organisation profile url
            education['organisation_profile'] = block.css('a::attr(href)').get(default='').split('?')[0]

            ## course details
            try:
                education['course_details'] = ''
                for text in block.css('h4 span::text').getall():
                    education['course_details'] = education['course_details'] + text.strip() + ' '
                education['course_details'] = education['course_details'].strip()
            except Exception as e:
                print("education --> course_details", e)
                education['course_details'] = ''

            ## description
            education['description'] = block.css('div.education__item--details p::text').get(default='').strip()
         
            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = date_ranges[1]
                elif len(date_ranges) == 1:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = 'present'
            except Exception as e:
                print("education --> time_ranges", e)
                education['start_time'] = ''
                education['end_time'] = ''

            item['education'].append(education)

        yield item
        