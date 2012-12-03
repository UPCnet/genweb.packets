from zope.component import getAdapter, getAdapters
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from genweb.packets.interfaces import IpacketDefinition


class packetView(BrowserView):

    template = ViewPageTemplateFile('templates/view.pt')

    def __call__(self):
        return self.template()


class packetEdit(BrowserView):

    template = ViewPageTemplateFile('templates/edit.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.available_ptypes = [adapter for adapter in getAdapters((self.context,), IpacketDefinition)]

    def __call__(self):
        if self.request.form:
            form = self.request.form
            packet_type = form.get("packet_type")
            adapter = getAdapter(self.context, IpacketDefinition, packet_type)
            values = {field:form[field] for field in adapter.fields}
            adapter.set_info(values)
            return self.request.response.redirect(self.context.absolute_url())
        else:
            return self.template()

    def getAvailablePacketsInfo(self):
        # return [dict(packet_type, name=packet_type[0], title=packet_type[1].title, description=packet_type[1].description) for packet_type in self.available_ptypes]
        return self.available_ptypes
