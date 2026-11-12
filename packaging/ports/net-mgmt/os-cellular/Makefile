PORTNAME=       os-cellular
PORTVERSION=    26.7.2
PORTREVISION=   32
CATEGORIES=     net-mgmt

MAINTAINER=     support@ds.co.ug
COMMENT=        OPNcell Open5GS management plugin for OPNsense
WWW=            https://github.com/opncell/opncell

LICENSE=        BSD2CLAUSE
USES=           python:run shebangfix
SHEBANG_FILES=  src/opnsense/scripts/opncell/*.py \
                src/opnsense/scripts/opncell/*.sh

USE_GITHUB=     yes
GH_ACCOUNT=     opncell
GH_PROJECT=     opncell
GH_TAGNAME=     v26.7

EXTRACT_DEPENDS=  git:devel/git
RUN_DEPENDS=    opncell-pymongo>=4.18.2:databases/opncell-pymongo \
                bash:shells/bash \
                open5gs>=2.8.0_1:net/opncell-open5gs \
                mongodb80>=8.0.34_1:databases/mongodb80 \
                opncell-mongosh>=2.14.0:databases/opncell-mongosh \
                ${PYTHON_PKGNAMEPREFIX}pyyaml>0:devel/py-pyyaml@${PY_FLAVOR} \
                ${PYTHON_PKGNAMEPREFIX}ujson>0:devel/py-ujson@${PY_FLAVOR}
ACTUAL-PACKAGE-DEPENDS= ${SH} ${FILESDIR}/package-dependencies.sh
NO_BUILD=       yes
NO_ARCH=        yes

WRKSRC_SUBDIR=  opncell
PKGPOSTUPGRADE= ${PKGDIR}/pkg-post-install

post-extract:
	cd ${WRKSRC}/.. && env GIT_CEILING_DIRECTORIES=${WRKDIR} ${LOCALBASE}/bin/git apply ${FILESDIR}/opncell-v26.7-update.diff && test -f opncell/src/opnsense/scripts/opncell/install_vips.php

	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-system-services.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-bind-labels.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-subscriber-feedback.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-delete-feedback.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-configurations-tab.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-service-restart.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-8.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-9.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-10.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-11.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-12.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-13.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-14.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-15.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-16.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-19.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-20.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-21.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-22.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-23.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-24.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-25.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-26.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-27.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-29.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-30.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-31.patch
	${PATCH} -V none -d ${WRKSRC}/src -p1 < ${FILESDIR}/opncell-release-32.patch
	${SED} -i "" -e 's|npx mongosh|${PREFIX}/bin/mongosh|g' ${WRKSRC}/src/opnsense/scripts/opncell/opncell_db.sh


do-install:
	${MAKE} -C ${WRKSRC} DESTDIR=${STAGEDIR} LOCALBASE=${PREFIX} \
	    PLUGIN_ABI=26.7 PLUGIN_VERSION=${PORTVERSION} PLUGIN_REVISION=${PORTREVISION} install
	${SED} -i "" -e '1s|.*|\#!${PREFIX}/bin/python3.13|' ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/query_log.py
	${CHMOD} 555 ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/read_subscriber.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/export_subscribers.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/active_logs.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/verify_boot.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/clear_log.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/query_log.py ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/hnet_management.py
	${MKDIR} ${STAGEDIR}${PREFIX}/share/opncell/installer
	${INSTALL_SCRIPT} ${FILESDIR}/installer/*.py ${STAGEDIR}${PREFIX}/share/opncell/installer/
	${SED} -i "" -e '1s|.*|\#!${PREFIX}/bin/python3.13|' ${STAGEDIR}${PREFIX}/share/opncell/installer/*.py
	cd ${FILESDIR}/defaults && ${COPYTREE_SHARE} . ${STAGEDIR}${PREFIX}/share/opncell/defaults
	${SED} -i "" -e '1s|.*|\#!${PREFIX}/bin/python3.13 -S|' ${STAGEDIR}${PREFIX}/opnsense/scripts/opncell/showUsers.py

.include <bsd.port.mk>
