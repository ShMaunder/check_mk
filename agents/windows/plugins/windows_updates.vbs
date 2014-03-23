' -----------------------------------------------------------------------------------------
' windows_updates.vbs - check_mk agent plugin to monitor pending windows updates indirectly
'
' To use this just place it in the plugins/ directory below the path of the
' check_mk_agent. After that an inventory run on the Nagios host should lead
' to a new inventorized service.
'
' Author: Lars Michelsen <lm@mathias-kettner.de>, 2011-03-21
' Editor: Patrick Schl�ter <ps@pdv-systeme.de>, 2011-08-21
'
' Updated by Phil Randal, 2012-09-21, to cache results using a randomised check interval
' of 16 to 24 hours
' Based on code here: http://www.monitoring-portal.org/wbb/index.php?page=Thread&threadID=23509
' Spawning a separate process to produce cached result (as in above forum discussion) caused me
' some issues, so I went for a simpler solution using only one script
'
' Updated by Bastian Kuhn, 2014-03-03: Removed all caching functions cause the current agent
' has a native caching support. Make shure that you activate caching for this script in check_mk.ini
' -----------------------------------------------------------------------------------------

Option Explicit

function readFromRegistry (strRegistryKey, strDefault )
    Dim WSHShell, value

    On Error Resume Next
    Set WSHShell = CreateObject("WScript.Shell")
    value = WSHShell.RegRead( strRegistryKey )

    if err.number <> 0 then
        readFromRegistry=strDefault
    else
        readFromRegistry=value
    end if

    set WSHShell = nothing
end function

Dim result, reboot, numImp, numOpt, important, opti
Dim updtSearcher, colDownloads, objEntry

Dim objFSO, stdout 
Set objFSO = WScript.CreateObject("Scripting.FileSystemObject")
Set stdout = objFSO.GetStandardStream(1)

Dim WSHShell
Set WSHShell = CreateObject("WScript.Shell")

Dim RebootTime
Dim RegPath

If CreateObject("Microsoft.Update.AutoUpdate").DetectNow <> 0 Then
    stdout.WriteLine("<<<windows_updates>>>")
    WScript.Quit()
End If

Set updtSearcher = CreateObject("Microsoft.Update.Session").CreateUpdateSearcher

RegPath = "HKEY_LOCAL_MACHINE\SOFTWARE\MICROSOFT\Windows\CurrentVersion\WindowsUpdate\Auto Update\"
RebootTime = ReadFromRegistry(RegPath & "NextFeaturedUpdatesNotificationTime","no_key")

reboot = 0
numImp = 0
numOpt = 0

If CreateObject("Microsoft.Update.SystemInfo").RebootRequired Then
    reboot = 1
End If

Set result = updtSearcher.Search("IsInstalled = 0 and IsHidden = 0")
Set colDownloads = result.Updates
For Each objEntry in colDownloads

    if objEntry.AutoSelectOnWebSites Then
       if numImp = 0 Then
           important = objEntry.Title
       else
           important = important & "; " & objEntry.Title
	   End If
		    numImp = numImp + 1
    Else
	    If numOpt = 0 Then
            opti = objEntry.Title
        Else
            opti = opti & "; " & objEntry.Title
	    End If
	    numOpt = numOpt + 1
    End If

Next

    stdout.WriteLine("<<<windows_updates>>>")
    stdout.WriteLine(reboot & " " & numImp & " " & numOpt)
    stdout.WriteLine(important)
    stdout.WriteLine(opti)
    stdout.WriteLine(RebootTime)
WScript.Quit()
