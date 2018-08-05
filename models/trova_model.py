from odoo import api, _, tools, fields, models, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from . import amount_to_text

class TrovaVivienda(models.Model):
	"""docstring for ClassName"""

	_name = 'trova.vivienda'
	_description='Formulario de Viviendas'


	def _folio_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return text
			

	name = fields.Char(string='Folio Real' , size=150, required=True)
	folio = fields.Char('Folio' , required=True, help='Este es el Folio', default=_folio_default)
	paquete = fields.Many2one('trova.vivienda.paquete',string='Paquete' , size=150, help='Este es el Paquete')
	subasta = fields.Many2one('trova.vivienda.suba', string='Subasta' , size=150, help='Esta es la Subasta')
	desarrollo = fields.Many2one('trova.vivienda.desa', string='Desarrollo' , size=150, help='Este es el desarrollo')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio' , size=150, required=True, help='El municipio')
	address = fields.Char('Direccion' , size=150, required=True, help='Esta es la Direccion')
	tipo_venta = fields.Many2one('trova.vivienda.tipo_venta', string='Tipo de Venta', help='Cual es el tipo de Venta')
	recamaras = fields.Integer('Numero de Recamaras',size=150, required=True, help='Este es el No. de Recamaras')
	fotos = fields.Boolean('Fotos', help='Fotos')
	clg = fields.Boolean('CLG',  help='CLG')
	aca = fields.Boolean('Avaluo Comercial anterior', help='Avaluo Comercial anterior')
	piso = fields.Boolean(string='Piso',  help='Piso')
	proteccion = fields.Boolean('Protecciones',  help='Protecciones')
	avalcat = fields.Boolean('Avaluo Catastral',  help='Avaluo Catastral')
	logo_viv = fields.Binary(string='Logo de encabezado')
	etapas = fields.Selection([('Disponible','Disponible'),
							   ('Invadida','Invadida'),
							   ('Poravaluo','Por avalúo'),
							   ('Porfirma','Por firmar'),
							   ('Firmada','Firmada'),
							   ('Cancelada','Cancelada')], help='Status',index=True, default='Disponible')
	precioventa = fields.Float('Precio de Venta' , required=True, help='Este sera el precio con el que se vendera la vivienda',  obj="res.currency")
	preciocompra = fields.Float('Precio de Compra' , required=True, help='Este sera el precio con el que se comprara la vivienda',  obj="res.currency")
	amount_to_text = fields.Char(compute='_get_amount_to_text', string='Monto en Texto', readonly=True,
                                 help='Amount of the invoice in letter', store=True)
	@api.one
	@api.depends('precioventa')
	def _get_amount_to_text(self):
		self.amount_to_text = amount_to_text.get_amount_to_text(self, self.precioventa, 'MXN')

class TrovaVivTitu(models.Model):
	
	_name = 'trova.vivienda.titu'
	_description = 'Pantalla de Titulacion'


	def _name_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda_titu" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return "Titulacion{}".format(text)


		

	name = fields.Char('Nombre' , size=150, required=True, default=_name_default)
	folio = fields.Many2one('trova.vivienda', string='Folio Real', required=True, help='Este es el Folio Real de la vivienda')
	etapas = fields.Selection([('Disponible','Disponible'),
							   ('Invadida','Invadida'),
							   ('Poravaluo','Por avalúo'),
							   ('Porfirma','Por firmar'),
							   ('Firmada','Firmada'),
							   ('Cancelada','Cancelada')], help='Status',index=True,default='Disponible' )
	confirmventa = fields.Char(string='Confirmacion de venta')
	presupuesto = fields.Many2one('sale.order', string='Presupuestos')
	asesor = fields.Many2one('res.users',string='Asesor', help='Lista de Asesores')
	tipocredito = fields.Selection([('tradicional','Tradicional'),('contado','Contado')], string='Confirmacion de venta Tipo de Credito')
	observaciones = fields.Selection([('habilitada','Habilitada'),('semihabilitada','Semihabilitada'),('sinhabilitar','Sin Habilitar')],string='Observaciones Vivienda', help='Observaciones')
	comentariostit = fields.Text(string='Comentarios Titulacion', help='Comentarios sobre la Titulacion')
	cliente = fields.Many2one('res.partner',string='Nombre del Cliente')
	nss = fields.Char(string='NSS', help='Ingresa el NSS')
	telefono = fields.Char(string='Telefono', help='Telefono Fijo')
	numtaria = fields.Char(string='Notaria', help='Notaria')
	numcredifona = fields.Integer(string='No. Credito Infonavit', help='Es el numero de credito Infonavit')
	fechacierre = fields.Date(string='Fecha Cierre')
	fechacaducacion = fields.Date(string='Fecha de Caducacion')

	@api.onchange('presupuesto')
	def onchange_pres(self):
		if self.presupuesto:			
			self.asesor = self.presupuesto.user_id.id
			self.folio = self.presupuesto.vivienda.id
			self.etapas = self.presupuesto.vivienda.etapas
			if(self.presupuesto.confirmation_date):
				self.confirmventa = str(self.presupuesto.confirmation_date)
			else:
				self.confirmventa='Pendiente'


	@api.onchange('cliente')
	def onchange_clien(self):
		if self.cliente:
			self.nss = self.cliente.nss
			self.telefono = self.cliente.phone

class TrovaVivDesarollo(models.Model):
	_name = 'trova.vivienda.desa'
	_description = 'Pantalla de Desarrollo'

	name = fields.Char('Nombre' , size=150, required=True)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	municipio = fields.Many2one('trova.vivienda.muni',string='Municipio' , size=150, required=True, help='El municipio')
class TrovaVivSaneamiento(models.Model):
	_name = 'trova.vivienda.sanea'
	_description = 'Pantalla de Saneamiento'


	def _name_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda_sanea" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return "Saneamiento{}".format(text)


	name = fields.Char(string='Nombre', size=150, required=True, default=_name_default)
	folioreal = fields.Many2one('trova.vivienda', string='Folio Real', required=True, help='Este es el Folio Real de la Vivienda')
	address = fields.Char('Dirección' , size=150, required=True, help='Esta es la Direccion')
	cuentapredial = fields.Char(string='Cuenta de predial', size=150, )
	mpp = fields.Integer(string='Monto Pagado Predial', size=10, help='Monto pagado del Predial')
	mpcp = fields.Integer(string='Monto Pagado CNA Predial', size=10, help='Monto pagado del CNA Predial')
	fechapp = fields.Date(string='Fecha Pago Predial', help='Fecha en la que se realizo el pago del Predial')
	mpcfe = fields.Integer(string='Monto Pagado CFE', help='Monto total pagado CFE')
	fechapcfe = fields.Date(string='Fecha de Pago CFE', size=150, help='Fecha en la que se realizo el pago del Predial')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	cuentagua = fields.Char(string='Cuenta Agua', size=125, help='Numero de cuenta del Agua')
	mpa = fields.Integer(string='Monto Pagado del Agua', size=10, help='Monto pagado del Agua')
	mpca = fields.Integer(string='Monto Pagado CNA Agua', size=10, help='Monto pagado del CNA Agua')
	fechapa = fields.Date(string='Fecha Pago Agua', help='Fecha en la que se realizo el pago del Agua')
	certioyp = fields.Char(string='Certificado no adeudo Obras y Pavimento', size=150, help='Certificado no adeudo Obras y Pavimento')
	certinof = fields.Char(string='Certificado alineamiento No. Oficial', size=150, help='Certificado alineamiento No. Oficial')
	certinadeu = fields.Char(string='Certificado No adeudo Tesorería', size=150, help='Certificado No adeudo Tesorería')
	no_oficial = fields.Char(string='No. Oficial', size=150, help='No. Oficial')
	certihipo = fields.Char(string='Certificado Hipotecario	', size=150, help='Certificado Hipotecario	')
	certifiscal = fields.Char(string='Certificado Fiscal', size=150, help='Certificado Fiscal')
	juntaurba = fields.Char(string='Junta Urbanización', size=150, help='Junta Urbanización')
	cartografico = fields.Char(string='Cartográfico	', size=150, help='Ubicacion Cartográfica')
	mpcarto = fields.Integer(string='Monto de pagado', help='Monto pagado por cartografico')
	fechacarto = fields.Date(string='Fecha Pago cartografico')
	mpnumofici = fields.Integer(string='Monto pagado por No. Oficial')
	fechanumofi = fields.Date(string='Fecha Pago No. Oficial')
	
	secretfinan = fields.Char(string='Secretaria de Finanzas')
	mpsecrefin = fields.Integer(string='Monto a pagar Finanzas')
	fechasecfin = fields.Date(string='Fecha de pago Finanzas')
	secretplanea = fields.Char(string='Secretaria de Planeacion')
	mpsecreplan = fields.Integer(string='Monto a pagar Planeacin')
	fechasecplan = fields.Date(string='Fecha de pago Planeacion')
	mpurba = fields.Integer(string='Monto a pagar Junta')
	fechaurba = fields.Date(string='Fecha de pago Junta')


	@api.onchange('folio')
	def onchange_folio(self):
		if self.folio:
			self.address = self.folio.address
			self.estado = self.folio.estado

class TrovaVivPaq(models.Model):
	_name = 'trova.vivienda.paquete'
	_description = 'Ventana de paquetes'

	name = fields.Char('Nombre' , size=150, required=True)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	corretaje = fields.Boolean(string='Corretaje')
	subastaprop = fields.Boolean(string='Subasta Propia')
	compradir = fields.Boolean(string='Compras Directas')
	prestaserv = fields.Boolean(string='Prestacion de Servicios')
class TrovaVivMuni(models.Model):
	_name = 'trova.vivienda.muni'
	_description = 'Pantalla de Municipio'

	name = fields.Char('Nombre' , size=150, required=True)
class TrovaVivSubasta(models.Model):
	"""docstring for TrovaTitu"""
	_name = 'trova.vivienda.suba'
	_description = 'Pantalla de subasta'

	name = fields.Char('Nombre' , size=150, required=True)
class TrovaVivTipoVenta(models.Model):
	"""docstring for TrovaTitu"""
	_name = 'trova.vivienda.tipo_venta'
	_description = 'Pantalla de Tipo de Venta'

	name = fields.Char('Nombre' , size=150, required=True)
class TrovaVivSale(models.Model):
	"""docstring for TrovaTitu"""
	_inherit = 'sale.order'

	vivienda = fields.Many2one('trova.vivienda', string="Folio Real de la Vivienda")
	address = fields.Char('Direccion' , size=150, required=True, help='Esta es la Direccion')
	fechacontrato = fields.Datetime(string='Fecha del contrato' , required=True, help='Puedes elegir una fecha de impresion para el contrato')
	etapas = fields.Selection([('Disponible','Disponible'),
							   ('Invadida','Invadida'),
							   ('Poravaluo','Por avalúo'),
							   ('Porfirma','Por firmar'),
							   ('Firmada','Firmada'),
							   ('Cancelada','Cancelada')], help='Status',index=True, default='Disponible')

	@api.onchange('vivienda')
	def onchange_vivienda(self):
		if self.vivienda:
			self.address = self.vivienda.address
			self.etapas = self.vivienda.etapas

class TrovaVivClientes(models.Model):
	_inherit = 'res.partner'

	fechanac=fields.Date(string='Fecha de Nacimiento')
	curp = fields.Char(string='CURP', size=18, help='Ingresa tu CURP')
	esque_credito = fields.Char(string='Esquema de Credito', size=100, help='Escribe tu Esquema de Credito')
	nss = fields.Integer(string='NSS', help='Ingresa el Numero de Seguro Social')
	estado_civil = fields.Selection([('soltero/a','Soltero/a'),
							   ('casado/a','Casado/a'),
							   ('divorciado/a','Divorciado/a'),
							   ('viudo/a','Viuda/a')], help='Estado civil')
	credito_conyu = fields.Boolean(string='Credito Conyugal')
	empresa = fields.Char(string='Empresa', size=100, help='Nombre de la empresa')
	numext = fields.Char(string='No Ext', size=100, help='Insgresa el numero exterior')
	entre = fields.Char(string='Entre', size=100, help='Entre que calles')
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio')
	cp = fields.Char(string='CP',size=10, help='Ingresa el Codigo Postal de tu zona')
	areaodep = fields.Char(string='Area o Departamento', size=100)
	extension = fields.Char(string='Extension', size=20)
	calle = fields.Char(string='Calle', size=100)
	numint = fields.Char(string='No Interior', size=23)
	colonia = fields.Char(string='Colonia', size=100)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	nrp = fields.Char(string='NRP')
	tel = fields.Char(string='Telefono')
	nombcompleto1 = fields.Char(string='Nombre Completo', size=100)
	tel_lada1 = fields.Char(string='Tel (lada)', help='Ingresa tu numero telefonico empezando con tu lada')
	refer1 = fields.Boolean(string='Referencia correcta 1')
	nombcompleto2 = fields.Char(string='Nombre Completo', size=100)
	tel_lada2 = fields.Char(string='Tel (lada)', help='Ingresa tu numero telefonico empezando con tu lada')
	refer2 = fields.Boolean(string='Referencia correcta 2')
	
