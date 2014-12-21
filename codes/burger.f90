! solve the Burger's equation on a finite-volume grid using
! using Godunov's method
!
! u_t + (0.5 u**2)_x = 0
!

program burger

  implicit none

  ! the number of zones (nx) and number of guardcells (ng)
  integer, parameter :: nx = 128
  integer, parameter :: ng = 2

  ! the domain size
  double precision, parameter :: xmin = 0.d0
  double precision, parameter :: xmax = 1.d0

  ! the CFL number
  double precision, parameter :: cfl = 0.8d0

  ! initial condition type
  integer, parameter :: inittype = 2
  
  ! slope type (1=godunov, 2=centered, 3=LW, 
  !             4=minmod limiting, 5=MC limiting, 6=superbee limiting)
  integer, parameter :: islopetype = 6

  ! maximum simulation time
  double precision, parameter :: tmax = 0.3d0


  double precision, dimension(2*ng + nx) :: x
  double precision, dimension(2*ng + nx) :: u, ul, ur, f

  double precision :: dx
  double precision :: time, dt


  ! setup the grid and set the initial conditions
  call grid(nx, ng, xmin, xmax, dx, x)

  call init(nx, ng, inittype, x, u)


  time = 0.d0

  call output(nx, ng, inittype, islopetype, time, x, u)


  ! evolution loop -- construct the interface states, solve the Riemann 
  ! problem, and update the solution to the new time level
  do while (time < tmax)

     call fillBC(nx, ng, u)

     call timestep(nx, ng, dx, cfl, u, dt)
     if (time + dt > tmax) then
        dt = tmax - time
     endif

     call states(nx, ng, dx, dt, islopetype, u, ul, ur)

     call riemann(nx, ng, ul, ur, f)

     call update(nx, ng, dx, dt, u, f)

     time = time + dt

  enddo
     
  call output(nx, ng, inittype, islopetype, time, x, u)


end program burger
  


!============================================================================
! grid: create the grid
!============================================================================
subroutine grid(nx, ng, xmin, xmax, dx, x)

  implicit none

  integer :: nx, ng
  double precision :: xmin, xmax

  double precision :: dx
  double precision, dimension(2*ng+nx) :: x

  integer :: i

  ! create the grid
  dx = (xmax - xmin)/dble(nx)

  do i = 1, 2*ng+nx
     x(i) = (i-ng-0.5d0)*dx + xmin
  enddo

  return
end subroutine grid



!============================================================================
! init: set the initial conditions
!============================================================================
subroutine init(nx, ng, inittype, x, u)

  implicit none

  integer :: nx, ng
  integer :: inittype

  double precision, dimension(2*ng+nx) :: x, u

  integer :: i, imin, imax

  double precision, parameter :: pi = 3.14159d0

  imin = ng+1
  imax = ng+nx

  ! loop over all the zones and set the initial conditions.  To be
  ! consistent with the finite-volume discretization, we should store
  ! the zone averages here, but, to second-order accuracy, it is
  ! sufficient to evaluate the initial conditions at the zone center.

  do i = imin, imax
     
     if (inittype == 1) then
        ! sin wave
        u(i) = sin(2.d0*pi*x(i))

     else if (inittype == 2) then
        ! square wave
        if (x(i) > 0.333d0 .and. x(i) < 0.666d0) then
           u(i) = 1.d0
        else
           u(i) = 0.d0
        endif

     else if (inittype == 3) then
        ! wave packet
        u(i) = sin(16.d0*pi*x(i))*exp(-36.d0*(x(i)-0.5d0)**2)

     endif

  enddo

  return
end subroutine init



!============================================================================
! output: write out the solution
!============================================================================
subroutine output(nx, ng, inittype, islopetype, time, x, u)

  implicit none

  integer :: nx, ng

  integer :: inittype, islopetype

  double precision :: time

  double precision, dimension(2*ng+nx) :: x, u

  character (len=4) :: time_string
  character (len=16) :: slope, init, res

  integer :: i, imin, imax

  imin = ng+1
  imax = ng+nx


  if (islopetype == 1) then
     slope = "upwind"
  else if (islopetype == 2) then
     slope = "centered"
  else if (islopetype == 3) then
     slope = "LW"
  else if (islopetype == 4) then 
     slope = "minmod"
  else if (islopetype == 5) then
     slope = "MC"
  else if (islopetype == 6) then
     slope = "superbee"
  endif

  if (inittype == 1) then
     init = "sine"
  else if (inittype == 2) then
     init = "tophat"
  else if (inittype == 3) then
     init = "packet"
  endif


  ! open the output file
  write (time_string, '(f4.2)') time
  write (res, '(i8)') nx

  open(unit=10, file="burger-"//trim(slope)//"-"//trim(init)//"-nx="//trim(adjustl(res))//"-t="//time_string, status="unknown")

  write (10,*) "# Burger's equation"
  write (10,*) "# init = ", inittype
  write (10,*) "# slope type = ", islopetype
  write (10,*) "# time = ", time


  do i = imin, imax
     write (10,*) x(i), u(i)
  enddo

  return
end subroutine output



!============================================================================
! fillBC: fill the boundary conditions
!============================================================================
subroutine fillBC(nx, ng, u)

  implicit none

  integer :: nx, ng
  double precision, dimension(2*ng+nx) :: u

  integer :: i, imin, imax

  imin = ng+1
  imax = ng+nx

  ! left boundary
  do i = 1, imin-1
     u(i) = u(imax-ng+i)
  enddo

  
  ! right boundary
  do i = imax+1, 2*ng+nx
     u(i) = u(i-imax+ng)
  enddo

  return
end subroutine fillBC
  
  

!============================================================================
! timestep: compute the new timestep
!============================================================================
subroutine timestep(nx, ng, dx, cfl, u, dt)
  
  implicit none

  integer :: nx, ng
  double precision :: dx
  double precision :: cfl
  double precision, dimension(2*ng+nx) :: u
  double precision :: dt
  
  integer :: i, imin, imax
  double precision, parameter :: SMALL = 1.d-12

  imin = ng+1
  imax = ng+nx
  
  dt = 1.e33
  do i = imin, imax
     dt = min(dt, dx/(abs(u(i)) + SMALL))
  enddo
  dt = cfl*dt
    
  return
end subroutine timestep
  


!============================================================================
! states: compute the interface states used in solving the Riemann problem
!============================================================================
subroutine states(nx, ng, dx, dt, islopetype, u, ul, ur)

  implicit none

  integer :: nx, ng
  integer :: islopetype

  double precision, dimension(2*ng+nx) :: u, ul, ur
  double precision, dimension(2*ng+nx) :: slope

  double precision :: slope1, slope2

  double precision :: a
  double precision :: dx, dt

  double precision :: minmod, maxmod

  integer :: i, imin, imax

  imin = ng+1
  imax = ng+nx


  ! compute the centered difference for linear slopes
  do i = imin-1, imax+1

     if (islopetype == 1) then

        ! Godunov's method (piecewise constant)
        slope(i) = 0.d0
        
     else if (islopetype == 2) then

        ! centered difference (equivalent to Fromm's method)
        slope(i) = 0.5*(u(i+1) - u(i-1))/dx

     else if (islopetype == 3) then

        ! downwind difference (equivalent to Lax-Wendroff)
        slope(i) = (u(i+1) - u(i))/dx

     else if (islopetype == 4) then

        ! minmod limited slope
        slope(i) = minmod((u(i) - u(i-1))/dx, (u(i+1) - u(i))/dx)

     else if (islopetype == 5) then

        ! MC limiter
        slope(i) = minmod(minmod(2.d0*(u(i) - u(i-1))/dx, &
                                 2.d0*(u(i+1) - u(i))/dx), &
                          0.5d0*(u(i+1) - u(i-1))/dx)

     else if (islopetype == 6) then

        ! superbee
        slope1 = minmod((u(i+1) - u(i))/dx, &
                        2.d0*(u(i) - u(i-1))/dx)

        slope2 = minmod(2.d0*(u(i+1) - u(i))/dx, &
                        (u(i) - u(i-1))/dx)

        slope(i) = maxmod(slope1, slope2)

     endif
  enddo


  ! for each interface, we want to construct the left and right
  ! states.  Here, interface i refers to the left edge of zone i
  
  ! interfaces imin to imax+1 affect the data in zones [imin,imax]
  do i = imin, imax+1

     ! the left state on the current interface comes from zone i-1.  
     ul(i) = u(i-1) + 0.5*dx*(1.d0 - u(i-1)*(dt/dx))*slope(i-1) 

     
     ! the right state on the current interface comes from zone i
     ur(i) = u(i) - 0.5*dx*(1.d0 + u(i)*(dt/dx))*slope(i)

  enddo

  return
end subroutine states
  


!============================================================================
! riemann: solve the Riemann problem
!============================================================================
subroutine riemann(nx, ng, ul, ur, f)

  implicit none

  integer :: nx, ng
  double precision, dimension(2*ng+nx) :: ul, ur, f
  double precision :: S, us

  integer :: i, imin, imax

  imin = ng+1
  imax = ng+nx


  ! loop over all the interfaces and solve the Riemann problem -- see Toro
  ! Ch. 2 and 3 for details on the solution
  do i = imin, imax+1
     if (ul(i) > ur(i)) then

        ! shock
        S = 0.5*(ul(i) + ur(i))

        if (S >= 0) then
           us = ul(i)
        else
           us = ur(i)
        endif

     else
        
        ! rarefaction
        if (ul(i) >= 0.0) then
           us = ul(i)
        else if (ur(i) <= 0.0) then
           us = ur(i)
        else
           us = 0.d0
        endif

     endif

     f(i) = 0.5*us*us

  enddo

  return
end subroutine riemann



!============================================================================
! update: conservatively update the solution to the new time level
!============================================================================
subroutine update(nx, ng, dx, dt, u, f)

  implicit none

  integer :: nx, ng

  double precision :: dx, dt

  double precision, dimension(2*ng+nx) :: u, f

  integer :: i, imin, imax

  imin = ng+1
  imax = ng+nx

  do i = imin, imax
     u(i) = u(i) + (dt/dx)*(f(i) - f(i+1))
  enddo
  
  return
end subroutine update



!============================================================================
! various limiter functions
!============================================================================
function minmod(a,b)

  implicit none

  double precision :: a, b
  double precision :: minmod

  if (abs(a) < abs(b) .and. a*b > 0.d0) then
     minmod = a
  else if (abs(b) < abs(a) .and. a*b > 0) then
     minmod = b
  else
     minmod = 0.d0
  endif

  return 
end function minmod



function maxmod(a,b)

  implicit none

  double precision :: a, b
  double precision :: maxmod

  if (abs(a) > abs(b) .and. a*b > 0.d0) then
     maxmod = a
  else if (abs(b) > abs(a) .and. a*b > 0) then
     maxmod = b
  else
     maxmod = 0.d0
  endif

  return 
end function maxmod
